import json
import requests

from .models           import Item, Ingredient, ItemIngredientMapping, ItemSkinType

from django.db         import transaction
from django.http       import JsonResponse, HttpResponse
from django.views      import View

from collections       import namedtuple

class PreProcessing(View):
    def get(self, request):

        ingredient_         = requests.get("https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/ingredient-data.json")
        ingredient_text    = json.loads(ingredient_.text)

        ingredient_fixture_list = []

        for count, data in enumerate(ingredient_text,1):
            if data["oily"] == "X":
                data["oily"] = -1
            elif data["oily"] == "":
                data["oily"] = 0
            elif data["oily"] == "O":
                data["oily"] = 1

            if data["dry"] == "X":
                data["dry"] = -1
            elif data["dry"] == "":
                data["dry"] = 0
            elif data["dry"] == "O":
                data["dry"] = 1

            if data["sensitive"] == "X":
                data["sensitive"] = -1
            elif data["sensitive"] == "":
                data["sensitive"] = 0
            elif data["sensitive"] == "O":
                data["sensitive"] = 1

            ingredient_fixture_list.append(
                {
                    "model"  : "item.ingredient",
                    "pk"     : count,
                    "fields" : {
                        "name"          :data["name"],
                        "oily"          :data["oily"],
                        "dry"           :data["dry"],
                        "sensitive"     :data["sensitive"]
                    }
                })

        with open('/home/ryu/바탕화면/hwahwe3/myapp/item/fixtures/ingredient-data.json', 'w', encoding='utf-8') as m:
            json.dump(ingredient_fixture_list, m, indent="\t", ensure_ascii=False)
            
        item         = requests.get("https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/item-data.json")
        item_text    = json.loads(item.text)

        item_fixture_list = [
            {
                "model"  : "item.item",
                "pk"     : data['id'],
                "fields" : {
                    "imageId"       :data["imageId"],
                    "name"          :data["name"],
                    "price"         :data["price"],
                    "gender"        :data["gender"],
                    "category"      :data["category"],
                    "monthlySales"  :data["monthlySales"]
                }
            } for data in item_text]

        with open('/home/ryu/바탕화면/hwahwe3/myapp/item/fixtures/item-data.json', 'w', encoding='utf-8') as m:
            json.dump(item_fixture_list, m, indent="\t", ensure_ascii=False)

        mapping_fixture_list = []
        item_text = list(item_text)
        count = 1

        for item_ingredient in item_text:
            for ingredient in ingredient_fixture_list:
                if ingredient['fields']['name'] in item_ingredient['ingredients']:
                    mapping_fixture_list.append(
                        {
                            "model"  : "item.itemIngredientMapping",
                            "pk"     : count,
                            "fields" : {
                                "item_id"       : item_ingredient['id'],
                                "ingredient_id" : ingredient['pk'],
                            }
                        }
                    )
                    count += 1

        with open('/home/ryu/바탕화면/hwahwe3/myapp/item/fixtures/mapping-data.json', 'w', encoding='utf-8') as m:
            json.dump(mapping_fixture_list, m, indent="\t", ensure_ascii=False)


        return JsonResponse({"MESSAGE":"SUCCESS"},status=200)

class GetSkinType(View):
    @transaction.atomic
    def get(self, request):
        item = Item.objects.all().prefetch_related('ingredients')

        for i in item:
            oily        = 0
            dry         = 0
            sensitive   = 0
            result_dict = {}

            for j in i.ingredients.all():
                oily      += j.oily
                dry       += j.dry
                sensitive += j.sensitive

            for x in ('oily', 'dry', 'sensitive'):
                result_dict[x] = locals()[x]

            if oily == dry and oily == sensitive:
                
                result = [ItemSkinType(
                    item             = i,
                    first_skin_type  = keys,
                    first_skin_score = result_dict[keys]
                ) for keys in result_dict]

                ItemSkinType.objects.bulk_create(result)

            elif oily == dry  and oily > sensitive:
                
                del result_dict['sensitive']
                result = [ItemSkinType(
                    item             = i,
                    first_skin_type  = keys,
                    first_skin_score = result_dict[keys]
                ) for keys in result_dict]

                ItemSkinType.objects.bulk_create(result)


            elif oily == sensitive and oily > dry:

                del result_dict['dry']
                result = [ItemSkinType(
                    item             = i,
                    first_skin_type  = keys,
                    first_skin_score = result_dict[keys]
                ) for keys in result_dict]

                ItemSkinType.objects.bulk_create(result)


            elif dry == sensitive and dry > oily:

                del result_dict['oily']
                result = [ItemSkinType(
                    item             = i,
                    first_skin_type  = keys,
                    first_skin_score = result_dict[keys]
                ) for keys in result_dict]

                ItemSkinType.objects.bulk_create(result)

            else :

                key_max_skin = max(result_dict.keys(), key=(lambda k: result_dict[k]))
                ItemSkinType.objects.create(
                    item             = i,
                    first_skin_type  = key_max_skin,
                    first_skin_score = result_dict[key_max_skin]
                )

        return JsonResponse({"MESSAGE":"SUCCESS"},status=200)



class itemList(View):

    def get(self, request):
        try:
    
            data = {
                "skin_type"          : "itemskintype__first_skin_type",
                "category"           : "category",
                "exclude_ingredient" : "itemingredientmapping__ingredient__name__in",
                "include_ingredient" : "itemingredientmapping__ingredient__name__in",
            }

            if 'skin_type' in request.GET and request.GET.get('skin_type') in ('oily', 'dry', 'sensitive'):
                params_dict    = {}
                ne_params_dict = {}
                page           = int(request.GET.get('page', 1))

                for k, v in request.GET.items():
                    if k == 'exclude_ingredient':
                        ex_list                 = request.GET.getlist('exclude_ingredient')
                        ne_params_dict[data[k]] = ex_list

                    elif k == 'include_ingredient':
                        in_list                 = request.GET.getlist('include_ingredient')
                        params_dict[data[k]]    = in_list

                    elif page:
                        pass

                    else:
                        params_dict[data[k]]    = v

                item = Item.objects.filter(**params_dict).exclude(**ne_params_dict)[(page-1)*50:page*50]

                if len(item) == 0:
                    return JsonResponse({'MESSAGE':'REQUEST_DATA_NOT_FOUND'}, status = 404)

                result =  [ 
                    {
                        "id"            : result.id,
                        "imgUrl"        : "https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/thumbnail/"+result.imageId+".jpg",
                        "name"          : result.name,
                        "price"         : result.price,
                        "ingredients"   : ",".join(value['name'] for value in result.ingredients.values()),
                        "monthlySales"  : result.monthlySales
                    }
                    for result in item]

                return JsonResponse(result, safe=False, status=200)
            
            else :
                return JsonResponse({"MESSAGE":"SKIN_TYPE_WRONG"}, status=401)
        
        except:
            JsonResponse({"MESSAGE":"BAD REQUESTS"}, status=404)

class itemDetail(View):
    def get(self, request, id):
            
        try:
            if id and id in range(1,1001):
                print(request.GET)
                if 'skin_type' in request.GET and request.GET.get('skin_type') in ('oily', 'dry', 'sensitive'):
                    skin_type = request.GET.get('skin_type')

                else:
                    return JsonResponse({"MESSAGE":"SKIN_TYPE_WRONG"}, status=401)
            else:
                return JsonResponse({"MESSAGE":"ID_OUT_OF_RANGE"}, status=401)
            
            item = Item.objects.get(id = id)
            result =  [ 
                        {
                            "id"            : item.id,
                            "imgUrl"        : "https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/image/"+item.imageId+".jpg",
                            "name"          : item.name,
                            "price"         : item.price,
                            "gender"        : item.gender,
                            "category"      : item.category,
                            "ingredients"   : ",".join(value['name'] for value in item.ingredients.values()),
                            "monthlySales"  : item.monthlySales
                        }
                        ]
            recommend_item = ItemSkinType.objects.filter(first_skin_type= skin_type, item__category = item.category).order_by('-first_skin_score')

            list_recommend_item = []
            for data in recommend_item:
                list_recommend_item.append((data.item.id ,data.item.imageId ,data.item.name ,data.first_skin_score , data.item.price))
            sorted_list= sorted(list_recommend_item, key = lambda x : (-x[3], x[4]))[0:3]
            
            Result = namedtuple('Result','id imageId name first_skin_score price')
            p1      = Result(*sorted_list[0])
            p2      = Result(*sorted_list[1])
            p3      = Result(*sorted_list[2])

            result.extend([
                            {
                            "id"            : p1.id,
                            "imgUrl"        : "https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/thumbnail/"+p1.imageId+".jpg",
                            "name"          : p1.name,
                            "price"         : p1.price,
                            },
                            {
                            "id"            : p2.id,
                            "imgUrl"        : "https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/thumbnail/"+p2.imageId+".jpg",
                            "name"          : p2.name,
                            "price"         : p2.price,
                            },
                            {
                            "id"            : p3.id,
                            "imgUrl"        : "https://grepp-programmers-challenges.s3.ap-northeast-2.amazonaws.com/2020-birdview/thumbnail/"+p3.imageId+".jpg",
                            "name"          : p3.name,
                            "price"         : p3.price,
                            }
                        ])
            return JsonResponse(result, safe=False, status=200)
        except:
            JsonResponse({"MESSAGE":"BAD REQUESTS"}, status=404)
