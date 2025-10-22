dico1 = {1:20, 2:20, 3:60}
dico2 = {1:20, 2:20, 3:60}
total = [{"F":60, "H":40}, {1:25, 2:25, 3:25, 4:25}]
groupe1 = [{"F":80, "H":20}, {1:45, 2:5, 3:35, 4:15}]
groupe2 = [{"F":70, "H":30}, {1:30, 2:20, 3:25, 4:25}]
groupe3 = [{"F":50, "H":50}, {1:25, 2:25, 3:35, 4:15}]
importance = [3, 1]
liste_groupe = [groupe1, groupe2, groupe3]

def score(dico1, dico2):
    res = 0
    if len(dico1) == len(dico2):
        for elem in dico1:
            res += abs(dico2[elem] - dico1[elem])
    return res

def get_diff_groupe(total, groupe):
    dist = 0
    if len(total) == len(groupe):
        for i in range(len(total)):
            dist += score(total[i], groupe[i])
    return dist

def score_tot(total, liste_group):
    dist_tot = 0
    for groupe in liste_group:
        dist_tot += get_diff_groupe(total, groupe)
    print(dist_tot)

score_tot(total, liste_groupe)
