# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 15:01:46 2019

@author: Leo Peach

Excerpt from AdcricPy
"""
import numpy as np
import matplotlib.pyplot as plt

class Mesh():
    def __init__(self, fort14):
        fort14 = self.parse_fort14(fort14)

        self.x = np.asarray(fort14.pop('x'))
        self.y = np.asarray(fort14.pop('y'))
        self.xy = np.vstack([self.x, self.y]).T
        self.z = np.asarray(fort14.pop('z'))
        self.elements = np.asarray(fort14.pop('elements'))

    def plot_mesh(self):
        fig = plt.figure()
        axes = fig.add_subplot(1,1,1)
        axes.tricontourf(self.x, self.y, self.elements, self.z)

        return axes

    def parse_fort14(self, path):
        """
        Read in fort14 mesh file
        """
        fort14 = dict()
        fort14['x'] = list()
        fort14['y'] = list()
        fort14['z'] = list()
        fort14['node_id'] = list()
        fort14['elements'] = list()
        fort14['element_id'] = list()
        # fort14['numberOfConnectedElements'] = list()
        fort14['OceanBoundaries'] = list()
        fort14['LandBoundaries'] = list()
        fort14['InnerBoundaries'] = list()
        fort14['InflowBoundaries'] = list()
        fort14['OutflowBoundaries'] = list()
        fort14['WeirBoundaries'] = list()
        fort14['CulvertBoundaries'] = list()
        with open(path, 'r') as f:
            fort14['description'] = "{}".format(f.readline())
            NE, NP = map(int, f.readline().split())
            _NP = len([])
            while _NP < NP:
                node_id, x, y, z = f.readline().split()
                fort14['node_id'].append(int(node_id)-1)
                fort14['x'].append(float(x))
                fort14['y'].append(float(y))
                fort14['z'].append(-float(z))
                _NP += 1
            _NE = len([])
            while _NE < NE:
                line = f.readline().split()
                fort14['element_id'].append(float(line[0]))
                # fort14['numberOfConnectedElements'].append(int(line[1]))
                if int(line[1]) != 3:
                    raise NotImplementedError('Package only supports '
                                              + 'triangular meshes for the '
                                              + 'time being.')
                fort14['elements'].append([int(x)-1 for x in line[2:]])
                _NE += 1
            # Assume EOF if NBOU is empty.
            try:
                NOPE = int(f.readline().split()[0])
            except IndexError:
                return fort14
            # For now, let -1 mean a self closing mesh
            # reassigning NBOU to 0 until further implementation is applied.
            if NOPE == -1:
                NOPE = 0
            _NOPE = len([])
            f.readline()  # Number of total open ocean nodes. Not used.
            while _NOPE < NOPE:
                fort14['OceanBoundaries'].append({'indexes': list()})
                NETA = int(f.readline().split()[0])
                _NETA = len([])
                while _NETA < NETA:
                    fort14['OceanBoundaries'][_NOPE]['indexes'].append(
                                                int(f.readline().split()[0])-1)
                    _NETA += 1
                _NOPE += 1
            NBOU = int(f.readline().split()[0])
            _NBOU = len([])
            f.readline()
            while _NBOU < NBOU:
                NVELL, IBTYPE = map(int, f.readline().split()[:2])
                _NVELL = 0
                if IBTYPE in [0, 10, 20]:
                    fort14['LandBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'indexes': list()})
                elif IBTYPE in [1, 11, 21]:
                    fort14['InnerBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'indexes': list()})
                elif IBTYPE in [2, 12, 22, 102, 122]:
                    fort14['InflowBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'indexes': list()})
                elif IBTYPE in [3, 13, 23]:
                    fort14['OutflowBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'indexes': list(),
                                    'barrier_heights': list(),
                                    'supercritical_flow_coefficients': list()})
    
                elif IBTYPE in [4, 24]:
                    fort14['WeirBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'front_face_indexes': list(),
                                    'back_face_indexes': list(),
                                    'barrier_heights': list(),
                                    'subcritical_flow_coefficients': list(),
                                    'supercritical_flow_coefficients': list()})
                elif IBTYPE in [5, 25]:
                    fort14['CulvertBoundaries'].append({
                                    'ibtype': IBTYPE,
                                    'front_face_indexes': list(),
                                    'back_face_indexes': list(),
                                    'barrier_heights': list(),
                                    'subcritical_flow_coefficients': list(),
                                    'supercritical_flow_coefficients': list(),
                                    'cross_barrier_pipe_heights': list(),
                                    'friction_factors': list(),
                                    'pipe_diameters': list()})
                else:
                    raise Exception('IBTYPE={} '.format(IBTYPE)
                                    + 'found in fort.14 not recongnized. ')
                while _NVELL < NVELL:
                    line = f.readline().split()
                    if IBTYPE in [0, 10, 20]:
                        fort14['LandBoundaries'][-1]['indexes'] \
                            .append(int(line[0])-1)
                    elif IBTYPE in [1, 11, 21]:
                        fort14['InnerBoundaries'][-1]['indexes'] \
                            .append(int(line[0])-1)
                    elif IBTYPE in [3, 13, 23]:
                        fort14['OutflowBoundaries'][-1]['indexes'] \
                            .append(int(line[0])-1)
                        fort14['OutflowBoundaries'][-1]['external_'
                                                        + 'barrier_heights'] \
                            .append(float(line[1]))
                        fort14['OutflowBoundaries'][-1]['supercritical_flow'
                                                        + '_coefficients'] \
                            .append(float(line[2]))
                    elif IBTYPE in [2, 12, 22, 102, 122]:
                        fort14['iflowBoundaries'][-1]['indexes'] \
                            .append(int(line[0])-1)
                    elif IBTYPE in [4, 24]:
                        fort14['WeirBoundaries'][-1]['front_face_indexes'] \
                            .append(int(line[0])-1)
                        fort14['WeirBoundaries'][-1]['back_face_indexes'] \
                            .append(int(line[1])-1)
                        fort14['WeirBoundaries'][-1]['barrier_heights'] \
                            .append(float(line[2]))
                        fort14['WeirBoundaries'][-1]['subcritical_'
                                                     + 'flow_coefficients'] \
                            .append(float(line[3]))
                        fort14['WeirBoundaries'][-1]['supercritical_'
                                                     + 'flow_coefficients'] \
                            .append(float(line[4]))
                    elif IBTYPE in [5, 25]:
                        fort14['CulvertBoundaries'][-1]['front_face_indexes'] \
                            .append(int(line[0])-1)
                        fort14['CulvertBoundaries'][-1]['back_face_indexes'] \
                            .append(int(line[1])-1)
                        fort14['CulvertBoundaries'][-1]['barrier_heights'] \
                            .append(float(line[2]))
                        fort14['CulvertBoundaries'][-1]['subcritical_flow_'
                                                        + 'coefficients'] \
                            .append(float(line[3]))
                        fort14['CulvertBoundaries'][-1]['supercritical_flow_'
                                                        + 'coefficients'] \
                            .append(float(line[4]))
                        fort14['CulvertBoundaries'][-1]['friction'
                                                        + 'Factor'] \
                            .append(float(line[5]))
                        fort14['CulvertBoundaries'][-1]['pipe_diameter'] \
                            .append(float(line[6]))
                    else:
                        Exception("Duck-typing error. "
                                  + "This exception should be unreachable.")
                    _NVELL += 1
                _NBOU += 1
        return fort14