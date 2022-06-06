import os
import json
from collections import defaultdict
from attr import get_run_validators
from cdlib import algorithms, classes, evaluation, readwrite
from sklearn import metrics



with open("dataset/custom_communities_corrected.json", "r", encoding="utf-8") as f:
    gt_communities = json.load(f)

results_dir = os.path.join(os.getcwd(),"results")
results = [i for i in os.listdir(results_dir) if i.endswith(".csv") and "angel" in i]



for result in results:
    
    prediction = readwrite.read_community_csv(os.path.join(results_dir,result), ",", str)

    with open(os.path.join(results_dir,result.split(".")[0]+".json"), "r", encoding="utf-8") as f:
        detected_communities = json.load(f)
    
    print()
    algo_name = result.split(".")[0]
    print(algo_name)
    print()

    if len(detected_communities) != 0:
        generalized_prediction = defaultdict(list)
        found_nodes = []
        for c in prediction.communities:
            found_nodes += c
        found_nodes = list(set(found_nodes))

        for i, pred in enumerate(prediction.communities):
            generalized_community = list(detected_communities[str(i)].keys())[0]
            generalized_prediction[generalized_community] += pred

        scores = {}
        weighted_scores = defaultdict(float)
        weighted_scores["support"] = len(found_nodes)
        for comm, pred in generalized_prediction.items():
            scores[comm] = defaultdict(float)
            tp, fp = 0,0
            gt = gt_communities["tracks"][comm]
            for track_id in pred:
                if track_id in gt:
                    tp += 1
                else:
                    fp += 1
            
            scores[comm]["precision"] = tp/(tp+fp)
            scores[comm]["recall"] = tp/len(gt)
            scores[comm]["f1"] = 2*(scores[comm]["precision"]*scores[comm]["recall"])/ \
                                (scores[comm]["precision"]+scores[comm]["recall"])
            scores[comm]["support"] = tp + fp

            weighted_scores["precision"] += scores[comm]["support"]*scores[comm]["precision"]/weighted_scores["support"]
            weighted_scores["recall"] += scores[comm]["support"]*scores[comm]["recall"]/weighted_scores["support"]
            weighted_scores["f1"] += scores[comm]["support"]*scores[comm]["f1"]/weighted_scores["support"]

        with open("results/scores_{}.txt".format(algo_name), "w", encoding="utf-8") as f:

            # total scores
            #print("CLASS", "PRECISION\t", "RECALL\t", "F1\t", "SUPPORT\t")
            f.write(f'{"CLASS":<{15}}{"PRECISION":>{10}}{"RECALL":>{10}}{"F1":>{10}}{"SUPPORT":>{10}}')
            f.write("\n")
            for com, s in scores.items():
                f.write(f'{com:<{15}}{round(s["precision"],2):>{10}}{round(s["recall"],2):>{10}}{round(s["f1"],2):>{10}}{round(s["support"],2):>{10}}')
                f.write("\n")
            f.write("\n")
            f.write(f'{"weighted avg":<{15}}{round(weighted_scores["precision"],2):>{10}}{round(weighted_scores["recall"],2):>{10}}{round(weighted_scores["f1"],2):>{10}}{weighted_scores["support"]:>{10}}')
    else:
        print("No communities detected...")
# gt_list = []
# pred_list = []
# for comm, ids in gt_communities:
#     if comm in generalized_prediction:
#         for i in ids:

#             gt_list.append(comm)
#             pred_list.append()
            
              

# report = metrics.classification_report(maj_labeling, truth_labeling)
    
# with open('results/results_angel.txt', 'w') as fl:
#     fl.write(report)
# print("Results saved...")
        