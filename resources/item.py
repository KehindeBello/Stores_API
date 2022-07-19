from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
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

    @jwt_required(fresh=True)
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
        claims = get_jwt()
        if not claims['is_admin']:
            return {"message": "Admin privilege required."}, 401
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
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"item": items}, 200
        
        return {
            "item": [item['name'] for item in items],
            "message" : "More details available on login"
        }, 200
    