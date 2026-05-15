-- Koya Restaurant — full menu seed
-- Run: psql -U koya -d koya -f /root/koy-repo/menu_seed.sql

-- STARTERS
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'starters','Arancini','Gorgonzola and turkey breast with tomato basil sauce','D850','/koya_menu_pics/aranchini.webp',0,10,''),
(gen_random_uuid()::text,'starters','Bao Buns with shredded beef','Pulled Beef, Onion, Carrot, Spiracha, sauce','D850','/koya_menu_pics/Bao_buns_with_shredded_beef.webp',0,20,''),
(gen_random_uuid()::text,'starters','Mini Burgers','3 Mini Burgers Smothered in Cheddar Sauce','D825','/koya_menu_pics/mimib.webp',0,30,''),
(gen_random_uuid()::text,'starters','Cauliflower velouté with smoked salmon','Silky whipped cauliflower velouté, delicately crowned with hand-shaved cold-smoked salmon and a drizzle of chive oil','D750','/koya_menu_pics/cauli.webp',0,40,''),
(gen_random_uuid()::text,'starters','Caesar salad',NULL,'D850','/koya_menu_pics/ceasarsalad.webp',0,50,''),
(gen_random_uuid()::text,'starters','Thiof Ceviche','Ceviche juice, Fresh marinated fish, Coriander, Red onion, Sweet potato paste, Avocado paste.','D875','/koya_menu_pics/thiofceviche.webp',0,60,''),
(gen_random_uuid()::text,'starters','Fritto misto','Breaded calamari and shrimp (panko), duo sauces (tartar & spicy)','D800','/koya_menu_pics/frittomisto.webp',0,70,''),
(gen_random_uuid()::text,'starters','Brick of goat cheese, with honey','Goat cheese wrapped in a brick leaf, small salad with dried figs, and honey-balsamic dressing','D800','/koya_menu_pics/brickofgoatcheese.webp',0,80,''),
(gen_random_uuid()::text,'starters','Carpaccio of beef filet','Thin slices of beef fillet, parmesan arugula pesto shavings, dressing.','D900','/koya_menu_pics/carpaccio.webp',0,90,'New');

-- MAIN COURSES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'mains','Chicken supreme','Grilled chicken escalope with its own jus','D1,100',NULL,0,10,''),
(gen_random_uuid()::text,'mains','Imported beef fillet','Hand-selected 200g centre-cut beef fillet, rested and finished with a bold house-ground black pepper jus','D1,950','/koya_menu_pics/importedbeeffillet.webp',0,20,''),
(gen_random_uuid()::text,'mains','Spicy Garlic Prawns','Spicy prawns with garlic and lemon','D1,700','/koya_menu_pics/spicygarlicprawns.webp',0,30,''),
(gen_random_uuid()::text,'mains','Roasted salmon steak with lemon beurre blanc sauce',NULL,'D2,100','/koya_menu_pics/roastedsalmon.webp',0,40,''),
(gen_random_uuid()::text,'mains','Burger','Fresh beef with tomato salad with caramelized onions and cheddar','D925','/koya_menu_pics/burger.webp',0,50,''),
(gen_random_uuid()::text,'mains','Whole Marinated Grilled Fish','Catch of the day','D1,500','/koya_menu_pics/wholemarinadedgrilledfish.webp',0,60,''),
(gen_random_uuid()::text,'mains','Black angus ribeye with garlic (300g)','300g prime ribeye heart, encrusted in garden herbs and slow-roasted with whole confit garlic','D2,350','/koya_menu_pics/blackangus.webp',0,70,''),
(gen_random_uuid()::text,'mains','Grilled lamb chops','With thyme honey sauce','D2,100',NULL,0,80,''),
(gen_random_uuid()::text,'mains','Grilled Thioff filet',NULL,'D1,500',NULL,0,90,'');

-- PIZZA
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'pizza','Pizza Koya','Fresh cream, poultry, mixed vegetables, mozzarella','D975','/koya_menu_pics/pizzakoya.webp',0,10,''),
(gen_random_uuid()::text,'pizza','Margherita','Tomato sauce, fior di latte mozzarella, basil','D800','/koya_menu_pics/margherita.webp',0,20,''),
(gen_random_uuid()::text,'pizza','Burratina','Tomato sauce, 150g burrata, pesto, basil persillade','D950','/koya_menu_pics/burratina.webp',0,30,''),
(gen_random_uuid()::text,'pizza','Salmon pizza','Sour cream, mozzarella, smoked salmon','D1,000','/koya_menu_pics/salmonpizza.webp',0,40,'');

-- SHARING MIX
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sharing','Sharing mix for two','Chicken skewers, bao, seafood rillettes, hummus, tzatziki, homemade bread','D2,200','/koya_menu_pics/sharingmixfortwo.webp',0,10,''),
(gen_random_uuid()::text,'sharing','Imported beef tomahawk (1.2 kg)','Served with 2 sides.','D8,000','/koya_menu_pics/importedbeeftomahawk.webp',0,20,''),
(gen_random_uuid()::text,'sharing','Whole marinated grilled fish for 2','Catch of the day','D2,500',NULL,0,30,''),
(gen_random_uuid()::text,'sharing','Whole marinated grilled Thiof for 2','Catch of the day','D3,000',NULL,0,40,'');

-- PASTA
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'pasta','Penne with chicken and mushroom cream sauce','Creamy Penne with chicken and mushrooms','D950',NULL,0,10,''),
(gen_random_uuid()::text,'pasta','Seafood Tagliatelle','Seafood duo (calamari''s and shrimps)','D1,300','/koya_menu_pics/seafoodtagleatel.webp',0,20,'');

-- SIDES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sides','Mashed potatoes','Creamy mashed potatoes',NULL,'/koya_menu_pics/mashedpotato.webp',0,10,''),
(gen_random_uuid()::text,'sides','White rice','Steamed white rice',NULL,'/koya_menu_pics/whiterice.webp',0,20,''),
(gen_random_uuid()::text,'sides','Sauteed vegetables','Sauteed seasonal vegetables',NULL,'/koya_menu_pics/sauteedvegetables.webp',0,30,''),
(gen_random_uuid()::text,'sides','Fries','Golden fries',NULL,'/koya_menu_pics/fries.webp',0,40,''),
(gen_random_uuid()::text,'sides','Green salad','Crisp mixed greens',NULL,'/koya_menu_pics/greensalad.webp',0,50,'');

-- SAUCES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'sauces','Shallot sauce',NULL,NULL,NULL,0,10,''),
(gen_random_uuid()::text,'sauces','Black pepper sauce',NULL,NULL,NULL,0,20,''),
(gen_random_uuid()::text,'sauces','Beurre blanc',NULL,NULL,NULL,0,30,'');

-- DESSERTS
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'desserts','Profiteroles with chocolate sauce','Pastry cream filling, whipped cream','D650','/koya_menu_pics/profiteroleswithchocklatesauce.webp',0,10,''),
(gen_random_uuid()::text,'desserts','French toast brioche','Salted caramel, red fruits, vanilla ice cream','D650','/koya_menu_pics/frenchtoastbriochee.webp',0,20,''),
(gen_random_uuid()::text,'desserts','Lemon cheesecake','Red fruit coulis','D700','/koya_menu_pics/lemoncheesecake.webp',0,30,''),
(gen_random_uuid()::text,'desserts','Chocolate lava cake','Warm dark-chocolate fondant with a molten centre, served with house-made vanilla ice cream','D700','/koya_menu_pics/chocklatelavacake.webp',0,40,''),
(gen_random_uuid()::text,'desserts','Mango pavlova','Meringue, Italian cream and mango.','D700',NULL,0,50,''),
(gen_random_uuid()::text,'desserts','Fluffy Pancakes','Red fruit pancakes with pistachio cream','D700','/koya_menu_pics/fluffypancakes.webp',0,60,'New');

-- SOFT DRINKS
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'softdrinks','Coke',NULL,'D200','/koya_menu_pics/coke.webp',0,10,''),
(gen_random_uuid()::text,'softdrinks','Diet Coke',NULL,'D250','/koya_menu_pics/dietcoke.webp',0,20,''),
(gen_random_uuid()::text,'softdrinks','Perrier Sparkling',NULL,'Small D200 / Large D250',NULL,0,30,''),
(gen_random_uuid()::text,'softdrinks','Fanta',NULL,'D200','/koya_menu_pics/fanta.webp',0,40,''),
(gen_random_uuid()::text,'softdrinks','Sprite',NULL,'D200','/koya_menu_pics/sprite.webp',0,50,''),
(gen_random_uuid()::text,'softdrinks','Red Bull',NULL,'D250','/koya_menu_pics/redbull.webp',0,60,''),
(gen_random_uuid()::text,'softdrinks','Imported water mondariz',NULL,'Small D125 / Large D200','/koya_menu_pics/importedwatermondariz.webp',0,70,''),
(gen_random_uuid()::text,'softdrinks','Schweppes tonic water',NULL,'D200','/koya_menu_pics/shhweppestonicwater.webp',0,80,'');

-- FRESH JUICES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'freshjuices','Fresh Orange Juice',NULL,'D400','/koya_menu_pics/freshorangejuice.webp',0,10,''),
(gen_random_uuid()::text,'freshjuices','Fresh Apple Juice',NULL,'D400','/koya_menu_pics/freshapplejuice.webp',0,20,''),
(gen_random_uuid()::text,'freshjuices','Fresh Pineapple Juice',NULL,'D400','/koya_menu_pics/freshpineapplejuice.webp',0,30,'');

-- LOCAL JUICES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'localjuices','Wonjo','Hibiscus juice','D150','/koya_menu_pics/wonjo.webp',0,10,''),
(gen_random_uuid()::text,'localjuices','Ginger Juice','Ginger juice','D150',NULL,0,20,''),
(gen_random_uuid()::text,'localjuices','Baobab','Baobab juice','D150',NULL,0,30,''),
(gen_random_uuid()::text,'localjuices','Daharr','Daharr juice','D150',NULL,0,40,'');

-- MILKSHAKES
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'milkshakes','Peachberry Shake','Vanilla, strawberry, peach, and milk','D450','/koya_menu_pics/peachberryshake.webp',0,10,''),
(gen_random_uuid()::text,'milkshakes','Strawberry Milkshake','Vanilla, strawberry, and milk','D450','/koya_menu_pics/strawberrymilkshake.webp',0,20,''),
(gen_random_uuid()::text,'milkshakes','Vanilla Milkshake','Vanilla, espresso, and milk','D450','/koya_menu_pics/VanillaMilkshake.webp',0,30,''),
(gen_random_uuid()::text,'milkshakes','Chocomint shake','Vanilla, green mint, chocolate, and milk','D450','/koya_menu_pics/chocomintshake.webp',0,40,'');

-- COFFEE (adds to existing 3 items)
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'coffee','American Coffee (Nescafe)',NULL,'D150','/koya_menu_pics/americancoffee.webp',0,58,''),
(gen_random_uuid()::text,'coffee','Mocha',NULL,'D375','/koya_menu_pics/mocha.webp',0,59,''),
(gen_random_uuid()::text,'coffee','Flavored iced coffee','Flavors: vanilla, caramel, hazelnut','D350','/koya_menu_pics/flavoredicedcoffee.webp',0,60,''),
(gen_random_uuid()::text,'coffee','Blue Iced Coffee',NULL,'D375','/koya_menu_pics/blueicedcoffee.webp',0,61,'');

-- Update existing coffee items with images
UPDATE menu_items SET image = '/koya_menu_pics/expresso.webp'    WHERE section = 'coffee' AND name = 'Espresso';
UPDATE menu_items SET image = '/koya_menu_pics/flavoredlatte.webp' WHERE section = 'coffee' AND name = 'Flavored Latte';
UPDATE menu_items SET image = '/koya_menu_pics/cappuccino.webp'  WHERE section = 'coffee' AND name = 'Cappuccino';

-- HOT TEA
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'hottea','Moroccan Mint Tea',NULL,'D150','/koya_menu_pics/moroccanminttea.webp',0,10,''),
(gen_random_uuid()::text,'hottea','Ginger Tea',NULL,'D150','/koya_menu_pics/gingertea.webp',0,20,''),
(gen_random_uuid()::text,'hottea','Tea Selection',NULL,'D150','/koya_menu_pics/teaselection.webp',0,30,'');

-- MOCKTAILS
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'mocktails','Classic Mojito','Cloudy Lemonade, Mint and Sparkling Water','D500','/koya_menu_pics/classicmojito.webp',0,10,''),
(gen_random_uuid()::text,'mocktails','Mango Daiquiri',NULL,'D550','/koya_menu_pics/mangodaiquiri.webp',0,20,''),
(gen_random_uuid()::text,'mocktails','Strawberry Daiquiri',NULL,'D550','/koya_menu_pics/straberrydaiquiri.webp',0,30,''),
(gen_random_uuid()::text,'mocktails','Pineapple Daiquiri',NULL,'D550','/koya_menu_pics/pineappledaiquiri.webp',0,40,''),
(gen_random_uuid()::text,'mocktails','Flavored Mojito','Available in Hibiscus, Mango, Lychee or Passion Fruit','D550','/koya_menu_pics/flavoredmojito.webp',0,50,''),
(gen_random_uuid()::text,'mocktails','Koya Sunset','Green Apple, hand-pressed Hibiscus, Tamarind and a splash of chilled Soda','D500',NULL,0,60,''),
(gen_random_uuid()::text,'mocktails','Tiki Taka','Passion Fruit, Pineapple Juice, Orange Juice and ginger','D550','/koya_menu_pics/tikitaka.webp',0,70,''),
(gen_random_uuid()::text,'mocktails','Star of the Evening','Salted Caramel Syrup, Fruit of Peach, Apple Juice and a Splash of Soda','D550','/koya_menu_pics/staroftheevening.webp',0,80,''),
(gen_random_uuid()::text,'mocktails','Spicy mandarin mule','Tangerine, falernum, lime juice and fevertree ginger beer','D550','/koya_menu_pics/spicymandarinemule.webp',0,90,''),
(gen_random_uuid()::text,'mocktails','Midnight orchard','Rose, passion fruit, goyave juice, lime juice and soda','D550','/koya_menu_pics/midnightorchard.webp',0,100,''),
(gen_random_uuid()::text,'mocktails','Sky','Curaçao bleu, almond, lime juice and soda','D550','/koya_menu_pics/sky.webp',0,110,''),
(gen_random_uuid()::text,'mocktails','Velvet','Strawberry, hibiscus, and ginger juice','D550','/koya_menu_pics/velvet.webp',0,120,''),
(gen_random_uuid()::text,'mocktails','Strawbasil','Strawberry, basilic, lemon juice, sparkling water','D500','/koya_menu_pics/strawbasil.webp',0,130,''),
(gen_random_uuid()::text,'mocktails','Cucumber Cooler','Green apple, cucumber, pineapple juice with soda','D500','/koya_menu_pics/cucumbercooler.webp',0,140,'');

-- ICED TEA
INSERT INTO menu_items (id,section,name,description,price,image,hidden,sort_order,badge) VALUES
(gen_random_uuid()::text,'icedtea','Lemon Iced Tea',NULL,'D400','/koya_menu_pics/lemonicedtea.webp',0,10,''),
(gen_random_uuid()::text,'icedtea','Raspberry Iced Tea',NULL,'D400','/koya_menu_pics/raspberryicedtea.webp',0,20,''),
(gen_random_uuid()::text,'icedtea','Peach Iced Tea',NULL,'D400','/koya_menu_pics/peachicedtea.webp',0,30,'');
