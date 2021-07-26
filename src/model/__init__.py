# from . import file
from . import schemas
from . import product
from . import user
from . import sales

# Acquirer = file.Acquirer
Schemas = schemas
ProductModel = product.Product
SizeModel = product.Sizes
ImageModel = product.ImagesDetail
TagModel = product.Tags
DiscountModel = product.Discount
StoreModel = user.Store
AddressModel = user.Address
UserModel = user.User
SalesModel = sales.Sales
DeliveryModel = sales.Delivery
CategoryModel = product.Category
SubCategoryModel = product.SubCategory