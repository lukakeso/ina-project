with open("results/scores_angel_communities.txt", 'r') as fp:    
    lines = fp.readlines()

    for line in lines:
        split = line.split()
        if len(split) >= 3:
            if split[0] == "weighted":
                print(split[0]+" "+split[1] + ' & ' + split[2] + ' & ' + split[3] + ' & ' + split[4] + ' & ' + split[5] + ' \\\\ \\hline')
            else:
                print(split[0] + ' & ' + split[1] + ' & ' + split[2] + ' & ' + split[3] + ' & ' + split[4] + ' \\\\ \\hline')