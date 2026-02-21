import json
from typing import Dict

json1 = input()
json2 = input()

json1_dict = json.loads(json1)
json2_dict = json.loads(json2)

def apply_patch(json1_dict: Dict, json2_dict: Dict):
    # keys_json1 = json1_dict.keys()
    # keys = list(keys_json1)
    results = []
    if len(json1_dict) > len(json2_dict):
        for key1, value1 in json1_dict.items():
            if key1 not in json2_dict:
                results.append([[None], key1, value1, None])
        return results
    # for key2, value2 in json2_dict.items():
    #     # if key2 not in keys_json1:
    #     #     json1_dict[key2] = value2
    #         # if key2 not in keys:
    #         #     keys.append(key2)
    #     if value2 is None:
    #         results.append([[None], key2, json1_dict.get(key2, None), None])

    #     elif isinstance(json1_dict.get(key2, None), dict) and isinstance(value2, dict):
    #         inner_results = apply_patch(json1_dict.get(key2, {}), value2)
    #         for result in inner_results:
    #             result[0].insert(0, key2)
    #         results.extend(inner_results)
    #         # if new_keys not in keys:
    #             # keys.append({key2: new_keys})
    #     else:
    #         results.append([[None], key2, json1_dict.get(key2, None), value2])
    #         # if key2 not in keys:
    #         #     keys.append(key2)
    # for key1, value1 in json1_dict.items():
    #     # if key2 not in keys_json1:
    #     #     json1_dict[key2] = value2
    #         # if key2 not in keys:
    #         #     keys.append(key2)
    #     if value1 is None:
    #         results.append([[None], key2, json1_dict.get(key2, None), None])

    #     elif isinstance(json2_dict.get(key1, None), dict) and isinstance(value1, dict):
    #         inner_results = apply_patch(value1, json2_dict.get(key1, {}))
    #         for result in inner_results:
    #             result[0].insert(0, key1)
    #         results.extend(inner_results)
    #         # if new_keys not in keys:
    #             # keys.append({key1: new_keys})
    #     else:
            
    #         results.append([[None], key1, json1_dict.get(key1, None), json2_dict.get(key1, None)])
    #         # if key2 not in keys:
    #         #     keys.append(key2)
    # return results
    
    for (key1,val1), (key2,val2) in zip(json1_dict.items(), json2_dict.items()):
        if isinstance(json2_dict.get(key1, None), dict) and isinstance(val1, dict):
            # print(1)
            inner_results = apply_patch(val1, json2_dict.get(key1, {}))
            for result in inner_results:
                result[0].insert(0, key1)
            
            # print(inner_results)
            for result in inner_results:
                if result in results:
                    continue
                else:
                    results.append(result)
        else:
            # print(2)
            new_result = [[None], key1, val1, json2_dict.get(key1, None)]
            if new_result not in results:
                results.append(new_result)
        if isinstance(json1_dict.get(key2, None), dict) and isinstance(val2, dict):
            # print(3)
            inner_results = apply_patch(json1_dict.get(key2, {}), val2)
            for result in inner_results:
                result[0].insert(0, key2)
            for result in inner_results:
                if result in results:
                    continue
                else:
                    results.append(result)
            
        else:
            # print(4)
            new_result = [[None], key2, json1_dict.get(key2, None), val2]
            if new_result not in results:
                results.append(new_result)
    return results
    


updated = apply_patch(json1_dict, json2_dict)
# print(updated)
# new_json_str = json.dumps(new_json, sort_keys=True)
final_results = []
for pair in updated:
    if pair[-2] == pair[-1]:
        continue
    else:
        temp_answer_title = []
        for ps in pair[:-2]:
            if isinstance(ps, list):
                for p in ps:
                    if p is not None:
                        temp_answer_title.append(p)
            else:
                temp_answer_title.append(ps)

        # temp_answer_new = ""
        if isinstance(pair[-1], list):
            # print(pair[-1])
            temp_answer_new = "[" + ",".join(map(str, pair[-1])) + "]"
        elif pair[-1] is None:
            temp_answer_new = "<missing>"
        else:
            temp_answer_new = pair[-1]
            
        
        # temp_answer_old = ""
        if isinstance(pair[-2], list):
            # print(pair[-2])
            temp_answer_old = "[" + ",".join(map(str, pair[-2])) + "]"
        elif pair[-2] is None:
            temp_answer_old = "<missing>"
        else:
            temp_answer_old = pair[-2]
        
        final_results.append(f'{".".join(temp_answer_title)} : {temp_answer_old} -> {temp_answer_new}')

if final_results:
    for result in final_results:
        print(result)
else:
    print("No differences")
