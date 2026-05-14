-- Koya Restaurant — full menu seed
-- Run: psql -U koya -d koya -f /root/koy-repo/menu_seed.sql

-- STARTERS
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'starters','Arancini','Gorgonzola and turkey breast with tomato basil sauce','D850',0,10,''),
(gen_random_uuid()::text,'starters','Bao Buns with shredded beef','Pulled Beef, Onion, Carrot, Spiracha, sauce','D850',0,20,''),
(gen_random_uuid()::text,'starters','Mini Burgers','3 Mini Burgers Smothered in Cheddar Sauce','D825',0,30,''),
(gen_random_uuid()::text,'starters','Cauliflower velouté with smoked salmon','Silky whipped cauliflower velouté, delicately crowned with hand-shaved cold-smoked salmon and a drizzle of chive oil','D750',0,40,''),
(gen_random_uuid()::text,'starters','Caesar salad',NULL,'D850',0,50,''),
(gen_random_uuid()::text,'starters','Thiof Ceviche','Ceviche juice, Fresh marinated fish, Coriander, Red onion, Sweet potato paste, Avocado paste.','D875',0,60,''),
(gen_random_uuid()::text,'starters','Fritto misto','Breaded calamari and shrimp (panko), duo sauces (tartar & spicy)','D800',0,70,''),
(gen_random_uuid()::text,'starters','Brick of goat cheese, with honey','Goat cheese wrapped in a brick leaf, small salad with dried figs, and honey-balsamic dressing','D800',0,80,''),
(gen_random_uuid()::text,'starters','Carpaccio of beef filet','Thin slices of beef fillet, parmesan arugula pesto shavings, dressing.','D900',0,90,'New');

-- MAIN COURSES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'mains','Chicken supreme','Grilled chicken escalope with its own jus','D1,100',0,10,''),
(gen_random_uuid()::text,'mains','Imported beef fillet','Hand-selected 200g centre-cut beef fillet, rested and finished with a bold house-ground black pepper jus','D1,950',0,20,''),
(gen_random_uuid()::text,'mains','Spicy Garlic Prawns','Spicy prawns with garlic and lemon','D1,700',0,30,''),
(gen_random_uuid()::text,'mains','Roasted salmon steak with lemon beurre blanc sauce',NULL,'D2,100',0,40,''),
(gen_random_uuid()::text,'mains','Burger','Fresh beef with tomato salad with caramelized onions and cheddar','D925',0,50,''),
(gen_random_uuid()::text,'mains','Whole Marinated Grilled Fish','Catch of the day','D1,500',0,60,''),
(gen_random_uuid()::text,'mains','Black angus ribeye with garlic (300g)','300g prime ribeye heart, encrusted in garden herbs and slow-roasted with whole confit garlic','D2,350',0,70,''),
(gen_random_uuid()::text,'mains','Grilled lamb chops','With thyme honey sauce','D2,100',0,80,''),
(gen_random_uuid()::text,'mains','Grilled Thioff filet',NULL,'D1,500',0,90,'');

-- PIZZA
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'pizza','Pizza Koya','Fresh cream, poultry, mixed vegetables, mozzarella','D975',0,10,''),
(gen_random_uuid()::text,'pizza','Margherita','Tomato sauce, fior di latte mozzarella, basil','D800',0,20,''),
(gen_random_uuid()::text,'pizza','Burratina','Tomato sauce, 150g burrata, pesto, basil persillade','D950',0,30,''),
(gen_random_uuid()::text,'pizza','Salmon pizza','Sour cream, mozzarella, smoked salmon','D1,000',0,40,'');

-- SHARING MIX
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sharing','Sharing mix for two','Chicken skewers, bao, seafood rillettes, hummus, tzatziki, homemade bread','D2,200',0,10,''),
(gen_random_uuid()::text,'sharing','Imported beef tomahawk (1.2 kg)','Served with 2 sides.','D8,000',0,20,''),
(gen_random_uuid()::text,'sharing','Whole marinated grilled fish for 2','Catch of the day','D2,500',0,30,''),
(gen_random_uuid()::text,'sharing','Whole marinated grilled Thiof for 2','Catch of the day','D3,000',0,40,'');

-- PASTA
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'pasta','Penne with chicken and mushroom cream sauce','Creamy Penne with chicken and mushrooms','D950',0,10,''),
(gen_random_uuid()::text,'pasta','Seafood Tagliatelle','Seafood duo (calamari''s and shrimps)','D1,300',0,20,'');

-- SIDES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sides','Mashed potatoes','Creamy mashed potatoes',NULL,0,10,''),
(gen_random_uuid()::text,'sides','White rice','Steamed white rice',NULL,0,20,''),
(gen_random_uuid()::text,'sides','Sauteed vegetables','Sauteed seasonal vegetables',NULL,0,30,''),
(gen_random_uuid()::text,'sides','Fries','Golden fries',NULL,0,40,''),
(gen_random_uuid()::text,'sides','Green salad','Crisp mixed greens',NULL,0,50,'');

-- SAUCES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sauces','Shallot sauce',NULL,NULL,0,10,''),
(gen_random_uuid()::text,'sauces','Black pepper sauce',NULL,NULL,0,20,''),
(gen_random_uuid()::text,'sauces','Beurre blanc',NULL,NULL,0,30,'');

-- DESSERTS
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'desserts','Profiteroles with chocolate sauce','Pastry cream filling, whipped cream','D650',0,10,''),
(gen_random_uuid()::text,'desserts','French toast brioche','Salted caramel, red fruits, vanilla ice cream','D650',0,20,''),
(gen_random_uuid()::text,'desserts','Lemon cheesecake','Red fruit coulis','D700',0,30,''),
(gen_random_uuid()::text,'desserts','Chocolate lava cake','Warm dark-chocolate fondant with a molten centre, served with house-made vanilla ice cream','D700',0,40,''),
(gen_random_uuid()::text,'desserts','Mango pavlova','Meringue, Italian cream and mango.','D700',0,50,''),
(gen_random_uuid()::text,'desserts','Fluffy Pancakes','Red fruit pancakes with pistachio cream','D700',0,60,'New');

-- SOFT DRINKS
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'softdrinks','Coke',NULL,'D200',0,10,''),
(gen_random_uuid()::text,'softdrinks','Diet Coke',NULL,'D250',0,20,''),
(gen_random_uuid()::text,'softdrinks','Perrier Sparkling',NULL,'Small D200 / Large D250',0,30,''),
(gen_random_uuid()::text,'softdrinks','Fanta',NULL,'D200',0,40,''),
(gen_random_uuid()::text,'softdrinks','Sprite',NULL,'D200',0,50,''),
(gen_random_uuid()::text,'softdrinks','Red Bull',NULL,'D250',0,60,''),
(gen_random_uuid()::text,'softdrinks','Imported water mondariz',NULL,'Small D125 / Large D200',0,70,''),
(gen_random_uuid()::text,'softdrinks','Schweppes tonic water',NULL,'D200',0,80,'');

-- FRESH JUICES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'freshjuices','Fresh Orange Juice',NULL,'D400',0,10,''),
(gen_random_uuid()::text,'freshjuices','Fresh Apple Juice',NULL,'D400',0,20,''),
(gen_random_uuid()::text,'freshjuices','Fresh Pineapple Juice',NULL,'D400',0,30,'');

-- LOCAL JUICES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'localjuices','Wonjo','Hibiscus juice','D150',0,10,''),
(gen_random_uuid()::text,'localjuices','Ginger Juice','Ginger juice','D150',0,20,''),
(gen_random_uuid()::text,'localjuices','Baobab','Baobab juice','D150',0,30,''),
(gen_random_uuid()::text,'localjuices','Daharr','Daharr juice','D150',0,40,'');

-- MILKSHAKES
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'milkshakes','Peachberry Shake','Vanilla, strawberry, peach, and milk','D450',0,10,''),
(gen_random_uuid()::text,'milkshakes','Strawberry Milkshake','Vanilla, strawberry, and milk','D450',0,20,''),
(gen_random_uuid()::text,'milkshakes','Vanilla Milkshake','Vanilla, espresso, and milk','D450',0,30,''),
(gen_random_uuid()::text,'milkshakes','Chocomint shake','Vanilla, green mint, chocolate, and milk','D450',0,40,'');

-- COFFEE (adds to existing 3 items)
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'coffee','American Coffee (Nescafe)',NULL,'D150',0,58,''),
(gen_random_uuid()::text,'coffee','Mocha',NULL,'D375',0,59,''),
(gen_random_uuid()::text,'coffee','Flavored iced coffee','Flavors: vanilla, caramel, hazelnut','D350',0,60,''),
(gen_random_uuid()::text,'coffee','Blue Iced Coffee',NULL,'D375',0,61,'');

-- HOT TEA
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'hottea','Moroccan Mint Tea',NULL,'D150',0,10,''),
(gen_random_uuid()::text,'hottea','Ginger Tea',NULL,'D150',0,20,''),
(gen_random_uuid()::text,'hottea','Tea Selection',NULL,'D150',0,30,'');

-- MOCKTAILS
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'mocktails','Classic Mojito','Cloudy Lemonade, Mint and Sparkling Water','D500',0,10,''),
(gen_random_uuid()::text,'mocktails','Mango Daiquiri',NULL,'D550',0,20,''),
(gen_random_uuid()::text,'mocktails','Strawberry Daiquiri',NULL,'D550',0,30,''),
(gen_random_uuid()::text,'mocktails','Pineapple Daiquiri',NULL,'D550',0,40,''),
(gen_random_uuid()::text,'mocktails','Flavored Mojito','Available in Hibiscus, Mango, Lychee or Passion Fruit','D550',0,50,''),
(gen_random_uuid()::text,'mocktails','Koya Sunset','Green Apple, hand-pressed Hibiscus, Tamarind and a splash of chilled Soda','D500',0,60,''),
(gen_random_uuid()::text,'mocktails','Tiki Taka','Passion Fruit, Pineapple Juice, Orange Juice and ginger','D550',0,70,''),
(gen_random_uuid()::text,'mocktails','Star of the Evening','Salted Caramel Syrup, Fruit of Peach, Apple Juice and a Splash of Soda','D550',0,80,''),
(gen_random_uuid()::text,'mocktails','Spicy mandarin mule','Tangerine, falernum, lime juice and fevertree ginger beer','D550',0,90,''),
(gen_random_uuid()::text,'mocktails','Midnight orchard','Rose, passion fruit, goyave juice, lime juice and soda','D550',0,100,''),
(gen_random_uuid()::text,'mocktails','Sky','Curaçao bleu, almond, lime juice and soda','D550',0,110,''),
(gen_random_uuid()::text,'mocktails','Velvet','Strawberry, hibiscus, and ginger juice','D550',0,120,''),
(gen_random_uuid()::text,'mocktails','Strawbasil','Strawberry, basilic, lemon juice, sparkling water','D500',0,130,''),
(gen_random_uuid()::text,'mocktails','Cucumber Cooler','Green apple, cucumber, pineapple juice with soda','D500',0,140,'');

-- ICED TEA
INSERT INTO menu_items (id,section,name,description,price,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'icedtea','Lemon Iced Tea',NULL,'D400',0,10,''),
(gen_random_uuid()::text,'icedtea','Raspberry Iced Tea',NULL,'D400',0,20,''),
(gen_random_uuid()::text,'icedtea','Peach Iced Tea',NULL,'D400',0,30,'');
