#!/usr/bin/env python3
"""Extrae información reproducible del URDF efectivo de MARTHA.

Ejemplos:
  python3 documentar_martha.py --topic /robot_description --out docs/figuras
  python3 documentar_martha.py --urdf martha.urdf --out docs/figuras --tcp gripper_tcp

El archivo de entrada debe ser URDF expandido (no Xacro sin procesar).
No evalúa colisiones, controladores, ni alcance alcanzable.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG, FG, MUTED = '#ffffff', '#273043', '#63728a'
ARM, FIXED, EE = '#4566a5', '#aab4c2', '#bd663a'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9, 'figure.facecolor': BG,
    'savefig.facecolor': BG, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.labelcolor': FG,
    'text.color': FG, 'xtick.color': FG, 'ytick.color': FG,
})


def get_from_topic(topic, timeout):
    """Lee el URDF publicado por robot_state_publisher; acepta publicación latched."""
    try:
        import rclpy
        from std_msgs.msg import String
        from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
    except ImportError as e:
        raise RuntimeError("Falta rclpy; ejecuta 'source /opt/ros/humble/setup.bash' "
                           "y 'source ~/ros2_ws/install/setup.bash'.") from e
    rclpy.init()
    node = rclpy.create_node('martha_documentacion_urdf')
    received = []
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                     reliability=ReliabilityPolicy.RELIABLE)
    sub = node.create_subscription(String, topic, lambda msg: received.append(msg.data), qos)
    try:
        start = time.monotonic()
        while not received and (time.monotonic() - start) < timeout:
            rclpy.spin_once(node, timeout_sec=0.3)
        if not received:
            raise RuntimeError(f"Sin descripción en {topic}. Revisa 'ros2 topic info {topic} -v' "
                               "y que robot_state_publisher esté ejecutándose.")
        return received[0]
    finally:
        node.destroy_subscription(sub)
        node.destroy_node()
        rclpy.shutdown()


def nums(s, default):
    return np.array([float(x) for x in s.split()], dtype=float) if s else np.array(default, dtype=float)


def joint_transform(j):
    ori = j.find('origin')
    xyz = nums(ori.get('xyz') if ori is not None else None, [0, 0, 0])
    roll, pitch, yaw = nums(ori.get('rpy') if ori is not None else None, [0, 0, 0])
    cr, sr, cp, sp, cy, sy = (math.cos(roll), math.sin(roll), math.cos(pitch),
                             math.sin(pitch), math.cos(yaw), math.sin(yaw))
    rot = np.array([
        [cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr],
        [sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr],
        [-sp, cp*sr, cp*cr],
    ])
    transform = np.eye(4)
    transform[:3, :3] = rot
    transform[:3, 3] = xyz
    return transform, xyz


def parse(xml):
    root = ET.fromstring(xml)
    if root.tag != 'robot':
        raise ValueError('El archivo no tiene raíz <robot> de URDF.')
    if any('macro' in e.tag or 'include' in e.tag for e in root.iter()):
        raise ValueError('Parece un Xacro sin expandir. Ejecuta xacro o usa --topic.')
    links = [e.get('name') for e in root.findall('link')]
    if not links:
        raise ValueError('El URDF no contiene enlaces <link>.')
    by_child = {}
    children = defaultdict(list)
    joint_rows = []
    for e in root.findall('joint'):
        parent_el, child_el = e.find('parent'), e.find('child')
        if parent_el is None or child_el is None:
            raise ValueError(f"Articulación sin padre/hijo: {e.get('name')}")
        parent, child = parent_el.get('link'), child_el.get('link')
        if child in by_child:
            raise ValueError(f'El URDF no es árbol: enlace hijo repetido {child}')
        typ = e.get('type', 'desconocido')
        limit = e.find('limit')
        origin, xyz = joint_transform(e)
        axis_el = e.find('axis')
        axis = nums(axis_el.get('xyz') if axis_el is not None else None, [1, 0, 0])
        entry = {'name': e.get('name'), 'type': typ, 'parent': parent, 'child': child,
                 'lower': float(limit.get('lower')) if limit is not None and limit.get('lower') is not None else None,
                 'upper': float(limit.get('upper')) if limit is not None and limit.get('upper') is not None else None,
                 'axis': axis.tolist(), 'origin_xyz': xyz.tolist(), 'T': origin}
        by_child[child] = entry
        children[parent].append(entry)
        joint_rows.append(entry)
    roots = [k for k in links if k not in by_child]
    if not roots:
        raise ValueError('No hay enlace raíz; revisa si el URDF tiene ciclos.')
    # Todas las transformaciones de los enlaces con q=0. No representa poses de simulación.
    poses = {r: np.eye(4) for r in roots}
    todo = roots[:]
    while todo:
        parent = todo.pop(0)
        for j in children[parent]:
            poses[j['child']] = poses[parent] @ j['T']
            todo.append(j['child'])
    return root.get('name', 'robot'), links, joint_rows, children, by_child, roots, poses


def choose_tcp(links, explicit):
    if explicit:
        if explicit not in links:
            raise ValueError(f"TCP '{explicit}' no aparece en el URDF. Busca el link real en articulaciones.csv")
        return explicit
    for t in ('gripper_tcp', 'tool0', 'tcp', 'ee_link', 'tool_link'):
        if t in links:
            return t
    return None


def tree_positions(children, roots):
    positions, counter = {}, [0]
    def visit(link, depth):
        kids = children.get(link, [])
        if not kids:
            y = counter[0]
            counter[0] += 1
        else:
            ys = [visit(j['child'], depth+1) for j in kids]
            y = sum(ys)/len(ys)
        positions[link] = (depth, y)
        return y
    for root in roots:
        visit(root, 0)
        counter[0] += 1
    return positions


def fig_tree(out, children, roots, joints):
    """Árbol orientado de arriba hacia abajo, legible también para cadenas largas."""
    pts = tree_positions(children, roots)
    max_depth = max(depth for depth, _ in pts.values())
    n_leaves = len({round(leaf, 4) for _, leaf in pts.values()})
    fig, ax = plt.subplots(figsize=(min(28, max(10, n_leaves*1.6)),
                                    min(30, max(6, (max_depth+1)*0.9))))
    for j in joints:
        d0, x0 = pts[j['parent']]
        d1, x1 = pts[j['child']]
        c = ARM if j['type'] != 'fixed' else FIXED
        ax.plot([x0, x1], [-d0, -d1], color=c, lw=1, alpha=0.75, zorder=1)
        ax.text((x0+x1)/2, -(d0+d1)/2, j['name'], fontsize=7,
                ha='center', color=c, zorder=3,
                bbox=dict(facecolor=BG, edgecolor='none', alpha=0.8, pad=0.1))
    for link, (depth, x) in pts.items():
        ax.text(x, -depth, link, fontsize=7.5, ha='center', va='center', zorder=4,
                bbox=dict(boxstyle='round,pad=0.38', facecolor='#edf2f8', edgecolor=ARM, lw=0.9))
    xs = [x for _, x in pts.values()]
    ax.set_xlim(min(xs)-0.85, max(xs)+0.85)
    ax.set_ylim(-max_depth-0.55, 0.65)
    ax.set_axis_off()
    ax.set_title('Jerarquía de enlaces y articulaciones (URDF)', loc='left', pad=15, fontweight='bold')
    fig.savefig(out/'fig_arbol_urdf.png', dpi=180, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)


def fig_limits(out, joints):
    for typ, unit, filename in [('revolute', 'rad', 'fig_limites_rotativas.png'),
                                ('prismatic', 'm', 'fig_limites_prismaticas.png')]:
        use = [j for j in joints if j['type'] == typ and j['lower'] is not None and j['upper'] is not None]
        if not use:
            continue
        fig, ax = plt.subplots(figsize=(10, max(3.2, len(use)*0.55+1.8)))
        for i, j in enumerate(use):
            ax.plot([j['lower'], j['upper']], [i, i], lw=6, color=ARM, solid_capstyle='round')
            ax.plot([j['lower'], j['upper']], [i, i], 'o', color=EE, ms=5)
            ax.annotate(f"{j['lower']:.3f} a {j['upper']:.3f} {unit}",
                        (j['upper'], i), xytext=(0, 9), textcoords='offset points',
                        fontsize=8, color=MUTED, ha='right', va='bottom')
        ax.set_yticks(range(len(use)), [j['name'] for j in use])
        ax.set_ylim(len(use)-0.25, -0.85)
        ax.axvline(0, ls=':', c=FIXED, zorder=0)
        ax.set_xlabel(f'Límite de posición ({unit})')
        ax.set_title(f'Articulaciones {"rotativas" if typ == "revolute" else "prismáticas"} del URDF',
                     loc='left', fontweight='bold')
        ax.grid(axis='x', alpha=0.15)
        fig.tight_layout()
        fig.savefig(out/filename, dpi=180, bbox_inches='tight')
        plt.close(fig)


def fig_chain(out, tcp, by_child, poses, root_limit):
    chain = [tcp]
    while chain[-1] in by_child and chain[-1] != root_limit:
        chain.append(by_child[chain[-1]]['parent'])
    if root_limit and chain[-1] != root_limit:
        raise ValueError(f"{root_limit} no es antepasado de {tcp}. No se genera cadena.")
    chain.reverse()
    P = np.array([poses[link][:3, 3] for link in chain])
    fig, axs = plt.subplots(1, 2, figsize=(13, 6))
    for ax, (idx, idz, title) in zip(axs, [(0, 2, 'Vista lateral: X–Z'),
                                           (1, 2, 'Vista frontal: Y–Z')]):
        ax.plot(P[:, idx], P[:, idz], '-o', color=ARM, ms=4, lw=1.7, zorder=3)
        for i, (link, pt) in enumerate(zip(chain, P)):
            joint = by_child.get(link)
            if idx == 1 and i not in (0, len(chain)-1):
                continue
            if i not in (0, len(chain)-1) and joint and joint['type'] == 'fixed':
                continue
            ax.annotate(link, (pt[idx], pt[idz]), xytext=(5, 7),
                        textcoords='offset points', fontsize=7, color=EE if link == tcp else FG)
        ax.scatter([P[-1, idx]], [P[-1, idz]], s=60, c=EE, zorder=4)
        ax.set_xlabel(('X' if idx == 0 else 'Y') + ' (m)')
        ax.set_ylabel('Z (m)')
        ax.set_title(title)
        ax.set_aspect('equal', adjustable='datalim')
        ax.margins(0.22)
        ax.grid(alpha=0.2)
    fig.suptitle(f'Cadena de marcos hasta {tcp} — geometría URDF en q=0 (no prueba movimiento)',
                 fontweight='bold')
    fig.tight_layout()
    fig.savefig(out/'fig_cadena_urdf.png', dpi=180, bbox_inches='tight')
    plt.close(fig)
    return {'cadena_hasta_tcp': chain, 'posicion_tcp_q0_m': P[-1].round(5).tolist(),
            'posiciones_en_cadena_q0_m': {k: v.round(5).tolist() for k, v in zip(chain, P)}}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group()
    src.add_argument('--urdf', type=Path, help='URDF ya expandido')
    src.add_argument('--topic', default=None, help='Tópico ROS 2, usualmente /robot_description')
    p.add_argument('--out', type=Path, default=Path('docs/figuras'), help='Carpeta de salida')
    p.add_argument('--tcp', help='Nombre real del enlace TCP en el URDF')
    p.add_argument('--base', help='Enlace base desde el cual mostrar la cadena al TCP (opcional)')
    p.add_argument('--timeout', type=float, default=12, help='Segundos para recibir el URDF desde ROS')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    xml = a.urdf.read_text(encoding='utf-8') if a.urdf else get_from_topic(a.topic or '/robot_description', a.timeout)
    name, links, joints, children, by_child, roots, poses = parse(xml)
    (a.out/'modelo_documentado.urdf').write_text(xml, encoding='utf-8')
    with (a.out/'articulaciones.csv').open('w', newline='', encoding='utf-8') as f:
        fields = ['name', 'type', 'parent', 'child', 'axis_xyz', 'origin_xyz_m', 'lower', 'upper', 'unit']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for j in joints:
            w.writerow({'name': j['name'], 'type': j['type'], 'parent': j['parent'],
                        'child': j['child'], 'axis_xyz': ' '.join(map(str, j['axis'])),
                        'origin_xyz_m': ' '.join(map(str, j['origin_xyz'])),
                        'lower': j['lower'], 'upper': j['upper'],
                        'unit': 'rad' if j['type'] in ('revolute', 'continuous') else
                                ('m' if j['type'] == 'prismatic' else '')})
    fig_tree(a.out, children, roots, joints)
    fig_limits(a.out, joints)
    tcp = choose_tcp(links, a.tcp)
    info = {'robot': name, 'numero_links': len(links), 'numero_articulaciones': len(joints),
            'raices': roots, 'tcp_elegido': tcp, 'tipos_articulacion':
            {typ: sum(1 for j in joints if j['type'] == typ) for typ in sorted({j['type'] for j in joints})},
            'nota': 'Información de URDF, no prueba de Gazebo, colisiones, control o movimiento.'}
    if tcp:
        info.update(fig_chain(a.out, tcp, by_child, poses, a.base))
    else:
        print('AVISO: no se detectó TCP conocido; usa --tcp NOMBRE_LINK para fig_cadena_urdf.png')
    (a.out/'inventario.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK: {name} — {len(links)} links, {len(joints)} joints; figuras en {a.out.resolve()}")
    for f in sorted(a.out.iterdir()):
        print(' -', f.name)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, ET.ParseError) as e:
        sys.exit(f'ERROR: {e}')
