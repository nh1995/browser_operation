import yaml

#yml stringを渡してtsvを返す
def convert_to_tsv(yml):
    yml_obj = _parse_yml(yml)
    if yml_obj is None:
        print("yml parse error.")    
        return None
    
    return _construct_tsv(yml_obj)
    

def _construct_tsv(yml_obj):
    

    for obj in yml_obj:
        if():

#yml操作用のオブジェクトを返す
def _parse_yml(yml):
    return yaml.safe_load(yml)