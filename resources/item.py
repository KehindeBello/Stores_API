from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="Field cannot be blank")

    parser.add_argument(
        'store_id',
        type=float,
        required=True,
        help="Item needs a Store_id")


    @jwt_required()
    def get(self, name):
        item = ItemModel.get_by_name(name)
        if item:
            return item.json()
        return {"message":"Item not found"}

    def post(self, name):
        if ItemModel.get_by_name(name):
            return {"message":f"An item with name {name} already exists"}

        data = Item.parser.parse_args()
        #data = request.get_json() #silent, force
        item = ItemModel(name, **data) #data["price"], data['store_id']

        try:
            item.save_to_db()
        except:
            return {"message":"An error seem to have occured"}, 500 #internal server error

        return item.json(), 201 #created

    @jwt_required()
    def delete(self,name):
        item = ItemModel.get_by_name(name)
        if item:
            item.delete_from_db()

        return {"message":"Item deleted"}

    def put(self,name):
        data = Item.parser.parse_args()
        item = ItemModel.get_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data) #data['price'], data['store_id']
            
        
        item.save_to_db()
        
        return item.json()


class ItemList(Resource):
    def get(self):
        return {"item": [item.json() for item in ItemModel.find_all()]}, 200
    #{"item": list(map(lambda x:x.json(),ItemModel.query.all()))}