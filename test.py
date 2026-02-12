import numpy as np

importance = np.array([10, 10, 20, 20, 30, 30, 40, 40], dtype=np.int64)

nb_ref = np.array([50, 50, 25, 75, 30, 70, 45, 55], dtype=np.int64)

mat_groupe = np.array([[50, 50, 25, 75, 30, 70, 45, 55], [30, 70, 30, 70, 30, 70, 30, 70], [70, 30, 70, 30, 70, 30, 70, 30]])

distance = (np.absolute(mat_groupe - nb_ref) * importance).sum(axis=1)

print(distance)

