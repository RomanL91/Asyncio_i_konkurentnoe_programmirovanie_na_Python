# 5.3 Определение схемы базы данных

# Чтобы начать выполнять запросы, нужна схема базы данных. Мы
# создадим простую схему products, моделирующую товары на складе
# интернет-магазина. Определим несколько сущностей, которые затем
# преобразуем в таблицы базы данных.

# Описание сущностей и их связей в БД
#    |-> Марка
#    |   Под маркой (brand) понимается производитель многих различных товаров. 
#    |   Например, Ford – марка, под которой производятся различные модели 
#    |   автомобилей (Ford F150, Ford Fiesta и т. д.).
#    |   
#    |-> Товар
#    |   Товар (product) ассоциирован с одной маркой, существует связь один-комногим 
#    |   между марками и товарами. Для простоты в нашей базе данных
#    |   у товара будет только название. В примере с Ford товаром будет компактный 
#    |   автомобиль Fiesta; его марка Ford. Кроме того, с каждым товаром
#    |   может быть связано несколько размеров и цветов. Совокупность размера
#    |   и цвета мы определим как SKU.
#    |   
#    |-> SKU
#    |   SKU расшифровывается как stock keeping unit (складская единица хранения). 
#    |   SKU представляет конкретный предмет, выставленный на продажу.
#    |   Например, для товара джинсы SKU может иметь вид: джинсы, размер: M,
#    |   цвет: синий или джинсы, размер: S, цвет: черный. Существует связь одинко-многим 
#    |   между товаром и SKU.
#    |   
#    |-> Размер товара
#    |   Товар может иметь несколько размеров (product size). В этом примере
#    |   будем предполагать, что всего есть три размера: малый (S), средний (M)
#    |   и большой (L). С каждым SKU ассоциирован один размер, поэтому существует 
#    |   связь один-ко-многим между размером товара и SKU.
#    |   
#    |-> Цвет товара
#        Товар может иметь несколько цветов (product color). В этом примере
#        будем предполагать, что цветов всего два: черный и синий. Существует
#        связь один-ко-многим между цветом товара и SKU.

# Теперь определим переменные, нужные для создания этой схемы. 
# С по­мощью asyncpg мы выполним соответствующие команды
# для создания базы данных о товарах. Поскольку размеры и цвета известны 
# заранее, вставим несколько записей в таблицы product_size
# и product_color. Мы будем ссылаться на эти переменные в последующих 
# листингах, чтобы не повторять длинные команды SQL.


CREATE_BRAND_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS brand(
    brand_id SERIAL PRIMARY KEY,
    brand_name TEXT NOT NULL
    );"""

CREATE_PRODUCT_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS product(
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand_id INT NOT NULL,
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
    );"""

CREATE_PRODUCT_COLOR_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS product_color(
    product_color_id SERIAL PRIMARY KEY,
    product_color_name TEXT NOT NULL
    );"""

CREATE_PRODUCT_SIZE_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS product_size(
    product_size_id SERIAL PRIMARY KEY,
    product_size_name TEXT NOT NULL
    );"""

CREATE_SKU_TABLE = \
    """
    CREATE TABLE IF NOT EXISTS sku(
    sku_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    product_size_id INT NOT NULL,
    product_color_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (product_size_id) REFERENCES product_size(product_size_id),
    FOREIGN KEY (product_color_id) REFERENCES product_color(product_color_id)
    );"""

COLOR_INSERT = \
    """
    INSERT INTO product_color VALUES(1, 'Blue');
    INSERT INTO product_color VALUES(2, 'Black');
    """

SIZE_INSERT = \
    """
    INSERT INTO product_size VALUES(1, 'Small');
    INSERT INTO product_size VALUES(2, 'Medium');
    INSERT INTO product_size VALUES(3, 'Large');
    """


# Далее
# 5.4 Выполнение запросов с помощью asyncpg
