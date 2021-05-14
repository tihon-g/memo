Назначение и возможности системы:

Система предназначена для создания и предоставления по запросу фотореалистичных рендеров (мебели)
со следующими оговорками
- с помощью blender (engine: eevee из-за высокой скорости) 
- с использованием заранее подготовленных 3d-моделей, где выставлен свет и ракурс камеры
скорость рендеринга составляет секунды, поэтому актуально использование созданных заранее рендеров.
для эффективного поиска заранее приготовленных рендеров используется спец.нейминг и раскадка по папочкам "качества"
- и свет и ракурс можно менять. но не в API


Запуск для разработки:
1. `python manage.py runserver`
2. `npm run start` в папке rendering/frontend/ для сборки фронтенда react 
3. `celery -A rendering worker -l INFO` для рендера


архитектура:

1. веб-сайт на django торчащий в интернет который предоставляет
- скетчбук https://sioux.8images.com/render/product/1/sketchbook/
- админку https://sioux.8images.com/admin/
- заказ больших ордеров https://sioux.8images.com/render/product/5/
- API, с главной функцией рендер по запросу: https://sioux.8images.com/api/render/12/config%3DFrame:1127-Pads:235-Bolsters:237/

2. rabbitMQ
- хранит и помогает распределять задания на рендер 

3. queue
скрипт запущенный на машине умеющей делать рендеры, читающий очередь и выкладывающий результаты куда скажут

Запущены systemd сервисы nginx + gunicorn + daphne + celery на проде

Какая база?
- sqlite (можно сделать на постгрес в любой момент)

Как задавать параметры типа quality и формат файла на выхлопе
- https://sioux.8images.com/admin/render/quality/ 
  страые не трогать чтоб не рушить базу и историю - можно делать новые, 
  флаг primary используется для выбора качества в sketchbook

Как уменьшить накладные расходы (и увеличить скорость)
Сейчас у меня получается где-то в районе 3.5-4 секунды на рендер, если через API в браузере. А с командной строки что-то около одной секунды
- играть качеством + настроить хронометраж, пока не знаю

Как глобально менять флаги в базе для тканей махарама на предмет "сегодня есть, а завтра нет". 
- 1. убрать finish: https://sioux.8images.com/admin/material/finish/ (признак archive)
- 2. настроить limitation включив в него желаемые паттерны: https://sioux.8images.com/admin/furniture/limitation/

настройки паттернов - как брать  дифьюзы нормали и рафнесы
- https://sioux.8images.com/admin/material/maps/
- если выбран режим pattern - значит для конкрентного финиша будет использоваться общий для паттерна файл
- если выбран режим finish - значит для конкрентного финиша будет использоваться уникальный для финиша файл



Базовые сущности (model, mesh, product, productkind=style, part)
Модель - состоит из мешей (в базе с маленькой буквы)
на каждый меш можно наложить материал или сделать прозрачным ( убрать )
меши модели упорядочены ( в базе )
это позволяет ввести нейминг для всех вариантов рендеров модели
<model_name>+<меш1name><материал на меш1>...<мешNname><материал на мешN>, если меша нет - материал 0

Можно сделать скетчбук который будет реализовывать произвольную раскраску 3D модели

но как выяснилось такое клиенту не надо. 
Ему нужна логика и взаимосвязь в расцветке, требование красить меши в связанные цвета и тп

ему нужен продукт

Продукт - как множество вариантов правильной(по мнению клиента) раскаски мешей модели.
клиенто-центричная 3D-модель

Логически делится на части parts(в базе с большой буквы, чтоб отличать от мешей и чтоб выводить в UI), которые расрашиваются в один цвет, зависимо или независимо друг от друга
таким образом состоят из мешей модели

в простом случае продукт реализация модели, а каждый part - меш, 

но во первых из модели можно сделать несколько продуктов, 
во вторых бывает что part состоит из различных мешей модели - приходится делать разные product style 
в каждом из которых расписывать конфигурацию

если сигнатура ( список названий parts ) видов продуктов совпадает - то их можно объединить в ux в едином продукте, не разделяя на виды в UX
если одна включает другую - то тоже можно объединить, сделав переключатель между style.

Для наглядности можно рассмотреть два продукта с двумя вариантами  kino stool/maru bench 5slats

1 kino stool.
логически, для скетчбука он состоит из parts - ножек и сидушки
но сидушка бывает разная - она может быть сплошь деревянной а может быть с линолеумной вставкой
при этом края вставки деревянные и всегда в цвет дерева ножек

получаем 4 меша (frame, top, insert, rim), 2 парта (Frame/Top) и 2 вида продукта 
  - Frame (covered:wood, meshes:frame) + Top (covered:wood, meshes:top), меши модели rim, insert - выключены
  - Frame (covered:wood, meshes:frame, rim) + Top (covered:linoleum, meshes:insert) , меш top - выключен

оба вида продукта объединяются в единый продукт - с понятным "скетчбуком" благодаря ограничению на раскраску rim
если б в продукте не было ограничения на rim - появилась бы третья степень свободы в раскраске и двумя parts обойтись было бы нельзя
но модель позволяет такие раскраски. и потенциально такие виды продукта возможны.
нейминг рендеров должен быть независим от видов продуктов и поэтому он не основан на parts: frame-<>/top-<>
а на мешах: frame-<>/top-<>/insert-<>/rim-<>

нейминг нужен беку, чтоб не переделывать уже готовые рендеры.
также нейминг использует мой скетчбук на django и знает весь список готовых на данный момент рендеров и не общаясь с беком знает заранее сколько есть рендеров по фильтру материалов выбранных пользователем в ux.
не происходит никакого ajax при смене фильтра - url к изображению уже известен

2. похожая и более сложная ситуация со скамейками maru - там тоже приходится вводить стиль продукта - "со столиком" и "без", потому что для логической части pads в зависимости от наличия стола приходится использовать разные меши 

именовать рендеры не по мешам а по part'ам идея плохая (мысль неочевидная, но доказанная)

таким образом сложилось описание продукта как перечисления его стилей kind каждый из которых описывается конфигурацией как массивом описания "частей"
"part": "Frame" - казалось бы все понятно, просто имя, однако по нему можно и нужно в рамках продуктового скетчбука объединять несколько styles (потом расскажу как и почему это очень важно)

defaultfinish - совсем очевидно - id материала который надо брать по умолчанию для скетчбука по каждую деталь
если не указано брать первый из списка finishes
null - потому что на беке нет этих данных. они там появятся когда получим от заказчика желаемую расцветку или заведем по данным старого скетчбука


"optional" - возможность убрать часть. очень важный параметр!)

"limited" - указывает на идентификатор ограничения на материал. ограничения хранятся в отдельном объекте limitation и могут ограничивать то что разрешает nature например какими конретными паттернами или даже финишами. 
примеры таких лимитейшн- "только светлые деревья" или только "mode или meld" или только матовый металл

colorchart - указывает на то, что финиш детали зависит от финиша предыдущей детали в конфигурации.
пока у нас используется лишь один колорчарт который единственным образом подбирает финиш mdf на обечайку в зависимости от финиша детали из дерева/линолеума к которому он примыкает.
поэтому в интерфейсе пользователя скетчбука продукта с этим колорчартом не надо спрашивать материал для детали им помеченной, как и скрывать наличие этой детали в принципе.
в конфигурации в перечислении parts деталь которая опеределяет другую должна идти сразу перед ней.
в будущем колорчарты могут и должны использоваться для реализации механизма походящих текстур
когда одни паттерны/финиши должны использоваться с какими-то определенными другими.
тогда колорчарт будет определять не единственный финиш а группу подходящих из которых надо выбрать пользователю.

"finishes" для частей не отмеченных колорчартом перечисляет все возможные финиши с учетом ограничения limited если оно есть
для colorcharted деталей - пусто, ибо динамически определяется колорчартом

для того чтоб строить ux как будто не хватает patterns - чтоб показать в ux палитры для выбора финиша.
Миша устроил панику и какой-то ненужный поиск
однако список паттернов получается автоматически из covered натур (у всех натур кроме фабрика как правило один паттерн)- если limited = null
или сразу из limitation - если он указан



Release plan
- websocket during rendering +
- quality list in api / request url +
- force rerender (with selected quality)
- names to db & setting def finishes via api
- queue ( rabbit? )
- server 
- manage versions of blender?
- another homepage
- websocket.js for local development and testing
- hide kill blender processes button


- tooltip on server
-- db stores data about models, products, materials & order for renders
-- queue manager: manage orders by running its on blender machines
-- blender: makes renders 

Redis used by Django Channels = websockects
