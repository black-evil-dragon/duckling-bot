from typing import Dict, List, Union
import json

UniversityStructure = Dict[str, Dict[int, Dict[str, str]]]
GROUP_IDS = {
    "ИМЕиКН": {
        2: {
            "4Б09 РПС-21": "231",
            "4Б09 ООС-21": "204",
        },
    },

    "ИМЕИТ": {
        2: {
            "5Б13 ЦТ-21": "629",
        }
    }
}

SubgroupStructure = Dict[str, int]
SUBGROUP_IDS = {
    "Первая подгруппа": 1,
    "Вторая подгруппа": 2,
    "Третья подгруппа": 3,
    "Четвертая подгруппа": 4,
    "Пятая подгруппа": 5,
    "Шестая подгруппа": 6,
}




class Group:

    @staticmethod
    def find_group_by_name(groups: List[Dict], group_name: str = "") -> str:
        result = []
    
        for group in groups:
            if isinstance(group, str) and (
                group_name.lower() in group.lower()
                or group_name.lower().replace("-", "").replace(" ", "") in group.lower().replace("-", "").replace(" ", "")
            ):
                result.append(group)
        
        return result
    

    @staticmethod
    def save_to_json(
        group_data: UniversityStructure = GROUP_IDS,
        subgroup_data: SubgroupStructure = SUBGROUP_IDS,
        filename: str = "./group_data.json"
    ) -> None:
        data = {
            "groups": group_data,
            "subgroups": subgroup_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_from_json(
        filename: str = "./group_data.json"
    ) -> Dict[str, Union[UniversityStructure, SubgroupStructure]]:

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:

            return {
                "groups": GROUP_IDS,
                "subgroups": SUBGROUP_IDS
            }
        except json.JSONDecodeError:

            return {
                "groups": GROUP_IDS,
                "subgroups": SUBGROUP_IDS
            }