#!/usr/bin/env python3
"""
Generate Benchmark 2 coordination items programmatically.
31 domains, ~20 items each, bilingual (en/zh).
"""

import json
from pathlib import Path

# =============================================================================
# Items organized by domain
# Each entry: (category, [4 options], culture, language)
# First option is the expected focal/salient choice
# =============================================================================

ITEMS = []

# ---------------------------------------------------------------------------
# Perception (weak culture, universal)
# ---------------------------------------------------------------------------
perception_items_en = [
    ("Primary Colors", ["Red", "Blue", "Green", "Yellow"]),
    ("Warm Colors", ["Red", "Orange", "Yellow", "Pink"]),
    ("Cool Colors", ["Blue", "Green", "Purple", "Teal"]),
    ("Basic Shapes", ["Circle", "Square", "Triangle", "Rectangle"]),
    ("Geometric Shapes", ["Triangle", "Square", "Pentagon", "Hexagon"]),
    ("Compass Directions", ["North", "South", "East", "West"]),
    ("Vertical Directions", ["Up", "Down", "Left", "Right"]),
    ("Spatial Relations", ["Above", "Below", "Left", "Right"]),
    ("Extremes of Size", ["Tiny", "Small", "Large", "Huge"]),
    ("Extremes of Temperature", ["Freezing", "Cold", "Hot", "Boiling"]),
    ("Extremes of Speed", ["Slow", "Fast", "Quick", "Rapid"]),
    ("Extremes of Weight", ["Feather", "Stone", "Boulder", "Mountain"]),
    ("Light and Dark", ["Dawn", "Dusk", "Midnight", "Noon"]),
    ("Sound Levels", ["Whisper", "Murmur", "Shout", "Scream"]),
    ("Texture Words", ["Smooth", "Rough", "Soft", "Hard"]),
    ("Basic Patterns", ["Stripe", "Dot", "Check", "Wave"]),
    ("Line Types", ["Straight", "Curved", "Zigzag", "Spiral"]),
    ("Depth Levels", ["Surface", "Shallow", "Deep", "Bottomless"]),
    ("Brightness Levels", ["Dim", "Glow", "Bright", "Blinding"]),
    ("Color Families", ["Red", "Blue", "Green", "Black"]),
]

perception_items_zh = [
    ("基本颜色", ["红色", "蓝色", "绿色", "黄色"]),
    ("暖色", ["红色", "橙色", "黄色", "粉色"]),
    ("冷色", ["蓝色", "绿色", "紫色", "青色"]),
    ("基本形状", ["圆形", "方形", "三角形", "矩形"]),
    ("几何图形", ["三角形", "正方形", "五边形", "六边形"]),
    ("方向", ["东", "南", "西", "北"]),
    ("空间方位", ["上", "下", "左", "右"]),
    ("大小极端", ["极小", "小", "大", "极大"]),
    ("温度极端", ["冰冷", "冷", "热", "滚烫"]),
    ("速度", ["缓慢", "快", "迅速", "飞速"]),
    ("明暗程度", ["昏暗", "微光", "明亮", "刺眼"]),
    ("声音大小", ["耳语", "低语", "喊叫", "尖叫"]),
    ("质感", ["光滑", "粗糙", "柔软", "坚硬"]),
    ("线条类型", ["直线", "曲线", "折线", "螺旋"]),
    ("亮度级别", ["暗淡", "微亮", "明亮", "耀眼"]),
    ("深浅程度", ["表面", "浅", "深", "极深"]),
    ("图案", ["条纹", "圆点", "格子", "波浪"]),
    ("颜色系列", ["红色", "蓝色", "绿色", "黑色"]),
    ("光线", ["晨光", "暮光", "正午", "午夜"]),
    ("声音频率", ["低沉", "柔和", "响亮", "尖锐"]),
]

# Colors
for cat, opts in perception_items_en[:5]:
    ITEMS.append({"domain": "Colors", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in perception_items_zh[:5]:
    ITEMS.append({"domain": "Colors", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Shapes
for cat, opts in perception_items_en[5:10]:
    ITEMS.append({"domain": "Shapes", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in perception_items_zh[5:10]:
    ITEMS.append({"domain": "Shapes", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Spatial Directions
for cat, opts in perception_items_en[10:15]:
    ITEMS.append({"domain": "Spatial Directions", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in perception_items_zh[10:15]:
    ITEMS.append({"domain": "Spatial Directions", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Extremes
for cat, opts in perception_items_en[15:20]:
    ITEMS.append({"domain": "Extremes", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in perception_items_zh[15:20]:
    ITEMS.append({"domain": "Extremes", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# ---------------------------------------------------------------------------
# Symbolism (weak culture)
# ---------------------------------------------------------------------------
symbolism_items_en = [
    ("Single Digit Numbers", ["7", "3", "5", "9"]),
    ("Round Numbers", ["10", "50", "100", "1000"]),
    ("Lucky Numbers", ["7", "8", "3", "11"]),
    ("Even Numbers", ["2", "4", "6", "8"]),
    ("Odd Numbers", ["3", "5", "7", "9"]),
    ("Times of Day", ["Morning", "Afternoon", "Evening", "Night"]),
    ("Days of the Week", ["Monday", "Wednesday", "Friday", "Sunday"]),
    ("Seasons", ["Spring", "Summer", "Autumn", "Winter"]),
    ("Months", ["January", "June", "September", "December"]),
    ("Basic Emotions", ["Happy", "Sad", "Angry", "Afraid"]),
    ("Positive Feelings", ["Joy", "Love", "Hope", "Gratitude"]),
    ("Negative Feelings", ["Anger", "Sadness", "Fear", "Disgust"]),
    ("Social Emotions", ["Pride", "Shame", "Guilt", "Envy"]),
    ("Calm Emotions", ["Peace", "Contentment", "Serenity", "Relief"]),
    ("Intense Emotions", ["Rage", "Euphoria", "Terror", "Ecstasy"]),
    ("Morning Hours", ["6 AM", "7 AM", "8 AM", "9 AM"]),
    ("Time Periods", ["Hour", "Day", "Week", "Month"]),
    ("Clock Times", ["12:00", "3:00", "6:00", "9:00"]),
    ("Holiday Seasons", ["Christmas", "New Year", "Halloween", "Easter"]),
    ("Year Divisions", ["January", "April", "July", "October"]),
]

symbolism_items_zh = [
    ("个位数字", ["7", "3", "5", "9"]),
    ("整数", ["10", "50", "100", "1000"]),
    ("幸运数字", ["8", "6", "9", "3"]),
    ("偶数", ["2", "4", "6", "8"]),
    ("奇数", ["3", "5", "7", "9"]),
    ("一天中的时间", ["早上", "下午", "傍晚", "深夜"]),
    ("一周的日子", ["周一", "周三", "周五", "周日"]),
    ("季节", ["春天", "夏天", "秋天", "冬天"]),
    ("月份", ["一月", "六月", "九月", "十二月"]),
    ("基本情绪", ["开心", "难过", "生气", "害怕"]),
    ("积极情绪", ["喜悦", "爱", "希望", "感恩"]),
    ("消极情绪", ["愤怒", "悲伤", "恐惧", "厌恶"]),
    ("社会情绪", ["骄傲", "羞耻", "内疚", "嫉妒"]),
    ("平静情绪", ["平和", "满足", "安宁", "释然"]),
    ("强烈情绪", ["暴怒", "狂喜", "恐惧", "兴奋"]),
    ("时段", ["清晨", "上午", "下午", "傍晚"]),
    ("时间单位", ["小时", "天", "周", "月"]),
    ("钟点", ["12点", "3点", "6点", "9点"]),
    ("节气", ["立春", "清明", "立秋", "冬至"]),
    ("年份划分", ["正月", "四月", "七月", "十月"]),
]

# Numbers
for cat, opts in symbolism_items_en[:5]:
    ITEMS.append({"domain": "Numbers", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in symbolism_items_zh[:5]:
    ITEMS.append({"domain": "Numbers", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Time Anchors
for cat, opts in symbolism_items_en[5:10]:
    ITEMS.append({"domain": "Time Anchors", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in symbolism_items_zh[5:10]:
    ITEMS.append({"domain": "Time Anchors", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Emotions
for cat, opts in symbolism_items_en[10:15]:
    ITEMS.append({"domain": "Emotions", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in symbolism_items_zh[10:15]:
    ITEMS.append({"domain": "Emotions", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Numbers extra
for cat, opts in symbolism_items_en[15:20]:
    ITEMS.append({"domain": "Numbers", "category": cat, "options": opts, "culture": "universal", "language": "en"})
for cat, opts in symbolism_items_zh[15:20]:
    ITEMS.append({"domain": "Numbers", "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# ---------------------------------------------------------------------------
# Biology (weak culture)
# ---------------------------------------------------------------------------
biology_animals_en = [
    ("Farm Animals", ["Cow", "Pig", "Sheep", "Chicken"]),
    ("Wild Animals", ["Lion", "Elephant", "Tiger", "Bear"]),
    ("Pet Animals", ["Dog", "Cat", "Fish", "Hamster"]),
    ("Sea Animals", ["Dolphin", "Shark", "Whale", "Octopus"]),
    ("Flying Animals", ["Eagle", "Owl", "Parrot", "Sparrow"]),
]
biology_animals_zh = [
    ("农场动物", ["牛", "猪", "羊", "鸡"]),
    ("野生动物", ["狮子", "大象", "老虎", "熊"]),
    ("宠物", ["狗", "猫", "鱼", "仓鼠"]),
    ("海洋动物", ["海豚", "鲨鱼", "鲸鱼", "章鱼"]),
    ("飞行动物", ["鹰", "猫头鹰", "鹦鹉", "麻雀"]),
]

biology_plants_en = [
    ("Garden Flowers", ["Rose", "Tulip", "Daisy", "Lily"]),
    ("Trees", ["Oak", "Pine", "Maple", "Birch"]),
    ("Indoor Plants", ["Cactus", "Fern", "Orchid", "Aloe"]),
    ("Wildflowers", ["Dandelion", "Sunflower", "Lavender", "Poppy"]),
    ("Shrubs", ["Hedge", "Azalea", "Hydrangea", "Bamboo"]),
]
biology_plants_zh = [
    ("花园花卉", ["玫瑰", "郁金香", "雏菊", "百合"]),
    ("树木", ["橡树", "松树", "枫树", "白桦"]),
    ("室内植物", ["仙人掌", "蕨类", "兰花", "芦荟"]),
    ("野花", ["蒲公英", "向日葵", "薰衣草", "罂粟花"]),
    ("灌木", ["灌木", "杜鹃", "绣球", "竹子"]),
]

biology_fruits_en = [
    ("Common Fruits", ["Apple", "Banana", "Orange", "Grape"]),
    ("Berries", ["Strawberry", "Blueberry", "Raspberry", "Blackberry"]),
    ("Tropical Fruits", ["Mango", "Pineapple", "Papaya", "Coconut"]),
    ("Stone Fruits", ["Peach", "Plum", "Cherry", "Apricot"]),
    ("Citrus Fruits", ["Orange", "Lemon", "Lime", "Grapefruit"]),
]
biology_fruits_zh = [
    ("常见水果", ["苹果", "香蕉", "橙子", "葡萄"]),
    ("浆果", ["草莓", "蓝莓", "树莓", "黑莓"]),
    ("热带水果", ["芒果", "菠萝", "木瓜", "椰子"]),
    ("核果", ["桃子", "李子", "樱桃", "杏"]),
    ("柑橘类", ["橙子", "柠檬", "青柠", "柚子"]),
]

biology_body_en = [
    ("Head Parts", ["Eye", "Nose", "Mouth", "Ear"]),
    ("Hand Parts", ["Finger", "Thumb", "Palm", "Wrist"]),
    ("Body Systems", ["Heart", "Brain", "Lung", "Stomach"]),
    ("Limbs", ["Arm", "Leg", "Hand", "Foot"]),
    ("External Features", ["Hair", "Skin", "Nail", "Teeth"]),
]
biology_body_zh = [
    ("头部器官", ["眼睛", "鼻子", "嘴巴", "耳朵"]),
    ("手部", ["手指", "拇指", "手掌", "手腕"]),
    ("内部器官", ["心脏", "大脑", "肺", "胃"]),
    ("四肢", ["手臂", "腿", "手", "脚"]),
    ("外部特征", ["头发", "皮肤", "指甲", "牙齿"]),
]

biology_senses_en = [
    ("Five Senses", ["Sight", "Hearing", "Touch", "Smell"]),
    ("Taste Types", ["Sweet", "Sour", "Salty", "Bitter"]),
    ("Touch Sensations", ["Hot", "Cold", "Rough", "Smooth"]),
    ("Visual Qualities", ["Bright", "Dark", "Colorful", "Plain"]),
    ("Sound Qualities", ["Loud", "Soft", "High", "Low"]),
]
biology_senses_zh = [
    ("五种感官", ["视觉", "听觉", "触觉", "嗅觉"]),
    ("味觉类型", ["甜", "酸", "咸", "苦"]),
    ("触感", ["热", "冷", "粗糙", "光滑"]),
    ("视觉特征", ["明亮", "黑暗", "多彩", "朴素"]),
    ("声音特征", ["响亮", "柔和", "高音", "低音"]),
]

for domain, en_list, zh_list in [
    ("Animals", biology_animals_en, biology_animals_zh),
    ("Plants", biology_plants_en, biology_plants_zh),
    ("Fruits", biology_fruits_en, biology_fruits_zh),
    ("Body Parts", biology_body_en, biology_body_zh),
    ("Senses", biology_senses_en, biology_senses_zh),
]:
    for cat, opts in en_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "en"})
    for cat, opts in zh_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# ---------------------------------------------------------------------------
# Artifacts (weak culture)
# ---------------------------------------------------------------------------
artifact_tools_en = [
    ("Hand Tools", ["Hammer", "Screwdriver", "Wrench", "Pliers"]),
    ("Cutting Tools", ["Knife", "Scissors", "Axe", "Saw"]),
    ("Measuring Tools", ["Ruler", "Scale", "Compass", "Thermometer"]),
    ("Writing Tools", ["Pen", "Pencil", "Marker", "Chalk"]),
    ("Garden Tools", ["Shovel", "Rake", "Hoe", "Trowel"]),
]
artifact_tools_zh = [
    ("手动工具", ["锤子", "螺丝刀", "扳手", "钳子"]),
    ("切割工具", ["刀", "剪刀", "斧头", "锯子"]),
    ("测量工具", ["尺子", "秤", "指南针", "温度计"]),
    ("书写工具", ["钢笔", "铅笔", "记号笔", "粉笔"]),
    ("园艺工具", ["铲子", "耙子", "锄头", "小铲"]),
]

artifact_clothing_en = [
    ("Upper Body Clothing", ["Shirt", "Jacket", "Sweater", "Coat"]),
    ("Lower Body Clothing", ["Pants", "Jeans", "Shorts", "Skirt"]),
    ("Footwear", ["Sneakers", "Boots", "Sandals", "Dress Shoes"]),
    ("Headwear", ["Cap", "Hat", "Beanie", "Helmet"]),
    ("Formal Wear", ["Suit", "Dress", "Tuxedo", "Gown"]),
]
artifact_clothing_zh = [
    ("上装", ["衬衫", "夹克", "毛衣", "外套"]),
    ("下装", ["裤子", "牛仔裤", "短裤", "裙子"]),
    ("鞋类", ["运动鞋", "靴子", "凉鞋", "皮鞋"]),
    ("帽子", ["鸭舌帽", "礼帽", "毛线帽", "头盔"]),
    ("正装", ["西装", "连衣裙", "燕尾服", "礼服"]),
]

artifact_vehicles_en = [
    ("Road Vehicles", ["Car", "Bus", "Truck", "Motorcycle"]),
    ("Two-Wheel Vehicles", ["Bicycle", "Motorcycle", "Scooter", "Skateboard"]),
    ("Water Vehicles", ["Boat", "Ship", "Canoe", "Yacht"]),
    ("Air Vehicles", ["Airplane", "Helicopter", "Balloon", "Glider"]),
    ("Public Transport", ["Bus", "Subway", "Taxi", "Train"]),
]
artifact_vehicles_zh = [
    ("道路车辆", ["汽车", "公交车", "卡车", "摩托车"]),
    ("两轮车", ["自行车", "摩托车", "滑板车", "滑板"]),
    ("水上交通", ["船", "轮船", "独木舟", "游艇"]),
    ("空中交通", ["飞机", "直升机", "热气球", "滑翔机"]),
    ("公共交通", ["公交车", "地铁", "出租车", "火车"]),
]

artifact_furniture_en = [
    ("Living Room Furniture", ["Sofa", "Table", "Chair", "Shelf"]),
    ("Bedroom Furniture", ["Bed", "Wardrobe", "Dresser", "Nightstand"]),
    ("Office Furniture", ["Desk", "Chair", "Filing Cabinet", "Bookshelf"]),
    ("Dining Furniture", ["Dining Table", "Chair", "Cabinet", "Sideboard"]),
    ("Storage Furniture", ["Cabinet", "Shelf", "Drawer", "Closet"]),
]
artifact_furniture_zh = [
    ("客厅家具", ["沙发", "桌子", "椅子", "书架"]),
    ("卧室家具", ["床", "衣柜", "梳妆台", "床头柜"]),
    ("办公家具", ["书桌", "椅子", "文件柜", "书架"]),
    ("餐厅家具", ["餐桌", "餐椅", "餐柜", "边柜"]),
    ("收纳家具", ["柜子", "架子", "抽屉", "衣橱"]),
]

for domain, en_list, zh_list in [
    ("Tools", artifact_tools_en, artifact_tools_zh),
    ("Clothing", artifact_clothing_en, artifact_clothing_zh),
    ("Vehicles", artifact_vehicles_en, artifact_vehicles_zh),
    ("Furniture", artifact_furniture_en, artifact_furniture_zh),
]:
    for cat, opts in en_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "en"})
    for cat, opts in zh_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# ---------------------------------------------------------------------------
# Places - Rooms (weak), Public Places (STRONG), Institutions (weak), Geographic (STRONG)
# ---------------------------------------------------------------------------
rooms_en = [
    ("Home Rooms", ["Bedroom", "Kitchen", "Bathroom", "Living Room"]),
    ("Kitchen Areas", ["Counter", "Stove", "Sink", "Refrigerator"]),
    ("Bathroom Features", ["Shower", "Toilet", "Sink", "Bathtub"]),
    ("Living Room Items", ["Sofa", "TV", "Carpet", "Window"]),
    ("Bedroom Furniture", ["Bed", "Closet", "Desk", "Mirror"]),
]
rooms_zh = [
    ("家庭房间", ["卧室", "厨房", "浴室", "客厅"]),
    ("厨房区域", ["台面", "炉灶", "水槽", "冰箱"]),
    ("浴室设施", ["淋浴", "马桶", "洗手台", "浴缸"]),
    ("客厅陈设", ["沙发", "电视", "地毯", "窗户"]),
    ("卧室家具", ["床", "衣柜", "书桌", "镜子"]),
]

institutions_en = [
    ("Educational Institutions", ["School", "University", "College", "Academy"]),
    ("Government Buildings", ["City Hall", "Court", "Post Office", "Library"]),
    ("Healthcare Facilities", ["Hospital", "Clinic", "Pharmacy", "Lab"]),
    ("Cultural Institutions", ["Museum", "Theater", "Gallery", "Library"]),
    ("Financial Institutions", ["Bank", "Insurance", "Stock Exchange", "Credit Union"]),
]
institutions_zh = [
    ("教育机构", ["学校", "大学", "学院", "研究院"]),
    ("政府建筑", ["市政厅", "法院", "邮局", "图书馆"]),
    ("医疗机构", ["医院", "诊所", "药房", "实验室"]),
    ("文化机构", ["博物馆", "剧院", "画廊", "图书馆"]),
    ("金融机构", ["银行", "保险", "证券交易所", "信用社"]),
]

for domain, en_list, zh_list in [
    ("Rooms", rooms_en, rooms_zh),
    ("Institutions", institutions_en, institutions_zh),
]:
    for cat, opts in en_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "en"})
    for cat, opts in zh_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "zh"})

# Public Places (STRONG culture)
public_places_us = [
    ("US Meeting Spots", ["Starbucks", "McDonald's", "Library", "Park"]),
    ("US Shopping Centers", ["Walmart", "Target", "Mall", "Costco"]),
    ("US Hangout Places", ["Coffee Shop", "Bar", "Gym", "Beach"]),
    ("US Public Squares", ["Times Square", "National Mall", "Central Park", "Pier"]),
    ("US Dining Venues", ["Restaurant", "Diner", "Food Court", "Cafe"]),
    ("US Entertainment Venues", ["Movie Theater", "Stadium", "Concert Hall", "Arcade"]),
    ("US Parks", ["Central Park", "Golden Gate Park", "Millennium Park", "Griffith Park"]),
    ("US Transport Hubs", ["Airport", "Train Station", "Bus Terminal", "Subway Station"]),
    ("US Recreational Places", ["Beach", "Hiking Trail", "Playground", "Pool"]),
    ("US Nightlife Spots", ["Bar", "Club", "Lounge", "Karaoke"]),
]
public_places_cn = [
    ("中国聚会场所", ["星巴克", "麦当劳", "图书馆", "公园"]),
    ("中国购物场所", ["淘宝", "京东", "万达广场", "超市"]),
    ("中国休闲场所", ["茶馆", "KTV", "健身房", "公园"]),
    ("中国公共广场", ["天安门广场", "人民广场", "中心广场", "步行街"]),
    ("中国餐饮场所", ["饭店", "小吃街", "食堂", "奶茶店"]),
    ("中国娱乐场所", ["电影院", "KTV", "网吧", "游乐场"]),
    ("中国公园", ["颐和园", "西湖", "人民公园", "植物园"]),
    ("中国交通枢纽", ["机场", "火车站", "地铁站", "汽车站"]),
    ("中国休闲去处", ["公园", "河边", "广场", "商场"]),
    ("中国夜生活", ["酒吧", "KTV", "夜市", "烧烤摊"]),
]

for cat, opts in public_places_us:
    ITEMS.append({"domain": "Public Places", "category": cat, "options": opts, "culture": "us", "language": "en"})
for cat, opts in public_places_cn:
    ITEMS.append({"domain": "Public Places", "category": cat, "options": opts, "culture": "china", "language": "zh"})

# Geographic Entities (STRONG culture)
geographic_us = [
    ("US Regions", ["Northeast", "South", "Midwest", "West"]),
    ("US Landmarks", ["Grand Canyon", "Statue of Liberty", "Mount Rushmore", "Golden Gate Bridge"]),
    ("US National Parks", ["Yellowstone", "Yosemite", "Grand Canyon", "Zion"]),
    ("US Rivers", ["Mississippi", "Colorado", "Missouri", "Ohio"]),
    ("US Mountain Ranges", ["Rockies", "Appalachians", "Sierra Nevada", "Cascades"]),
    ("US Coastlines", ["East Coast", "West Coast", "Gulf Coast", "Great Lakes"]),
    ("US Climate Zones", ["Tropical", "Arid", "Temperate", "Continental"]),
    ("US States by Size", ["Alaska", "Texas", "California", "Montana"]),
    ("US Islands", ["Hawaii", "Manhattan", "Long Island", "Maui"]),
    ("US Borders", ["Canada", "Mexico", "Pacific Ocean", "Atlantic Ocean"]),
]
geographic_cn = [
    ("中国地区", ["华东", "华南", "华北", "西南"]),
    ("中国名胜", ["长城", "故宫", "兵马俑", "黄山"]),
    ("中国名山", ["泰山", "黄山", "华山", "峨眉山"]),
    ("中国河流", ["长江", "黄河", "珠江", "淮河"]),
    ("中国湖泊", ["西湖", "太湖", "鄱阳湖", "洞庭湖"]),
    ("中国气候带", ["热带", "亚热带", "温带", "寒带"]),
    ("中国省份", ["广东", "江苏", "山东", "四川"]),
    ("中国城市带", ["长三角", "珠三角", "京津冀", "成渝"]),
    ("中国海", ["南海", "东海", "黄海", "渤海"]),
    ("中国边界", ["俄罗斯", "蒙古", "印度", "越南"]),
]

for cat, opts in geographic_us:
    ITEMS.append({"domain": "Geographic Entities", "category": cat, "options": opts, "culture": "us", "language": "en"})
for cat, opts in geographic_cn:
    ITEMS.append({"domain": "Geographic Entities", "category": cat, "options": opts, "culture": "china", "language": "zh"})

# ---------------------------------------------------------------------------
# Norms - Family Roles (weak), Occupations (weak), Social Norms (STRONG)
# ---------------------------------------------------------------------------
family_en = [
    ("Immediate Family", ["Mother", "Father", "Sister", "Brother"]),
    ("Extended Family", ["Grandmother", "Grandfather", "Aunt", "Uncle"]),
    ("In-Law Relations", ["Mother-in-law", "Father-in-law", "Sister-in-law", "Brother-in-law"]),
    ("Parent-Child Roles", ["Parent", "Child", "Sibling", "Cousin"]),
    ("Generational Roles", ["Grandparent", "Parent", "Child", "Grandchild"]),
]
family_zh = [
    ("直系亲属", ["妈妈", "爸爸", "姐妹", "兄弟"]),
    ("旁系亲属", ["奶奶", "爷爷", "阿姨", "叔叔"]),
    ("姻亲关系", ["婆婆", "岳父", "嫂子", "姐夫"]),
    ("亲子角色", ["父母", "子女", "兄弟姐妹", "表亲"]),
    ("世代角色", ["祖辈", "父辈", "子女", "孙辈"]),
]

occupations_en = [
    ("Medical Professions", ["Doctor", "Nurse", "Surgeon", "Pharmacist"]),
    ("Education Professions", ["Teacher", "Professor", "Principal", "Tutor"]),
    ("Tech Professions", ["Programmer", "Designer", "Engineer", "Analyst"]),
    ("Service Professions", ["Waiter", "Cashier", "Receptionist", "Driver"]),
    ("Creative Professions", ["Artist", "Writer", "Musician", "Actor"]),
]
occupations_zh = [
    ("医疗职业", ["医生", "护士", "外科医生", "药剂师"]),
    ("教育职业", ["教师", "教授", "校长", "辅导员"]),
    ("科技职业", ["程序员", "设计师", "工程师", "分析师"]),
    ("服务职业", ["服务员", "收银员", "前台", "司机"]),
    ("创意职业", ["画家", "作家", "音乐家", "演员"]),
]

social_norms_us = [
    ("US Table Manners", ["Don't talk with mouth full", "Elbows off table", "Use napkin", "Chew quietly"]),
    ("US Greetings", ["Handshake", "Wave", "Hug", "Nod"]),
    ("US Dining Etiquette", ["Wait for everyone", "No phones at table", "Tip 20%", "Say please/thank you"]),
    ("US Public Behavior", ["Queue in line", "Hold door open", "Say excuse me", "Don't litter"]),
    ("US Gift Customs", ["Birthday gifts", "Christmas gifts", "Wedding gifts", "Thank you notes"]),
    ("US Meeting Norms", ["Arrive on time", "Make eye contact", "Business cards", "Firm handshake"]),
    ("US Dress Codes", ["Business suit", "Smart casual", "Casual", "Formal"]),
    ("US Conversation Norms", ["Small talk", "Eye contact", "Personal space", "No interrupting"]),
    ("US Holiday Customs", ["Turkey on Thanksgiving", "Fireworks on July 4th", "Trick-or-treat", "Easter eggs"]),
    ("US Wedding Customs", ["White dress", "Best man", "Wedding cake", "First dance"]),
]
social_norms_cn = [
    ("中国餐桌礼仪", ["不吧唧嘴", "长辈先动筷", "筷子不插饭", "不翻菜"]),
    ("中国问候方式", ["握手", "点头", "鞠躬", "拱手"]),
    ("中国用餐礼仪", ["等人齐了再吃", "敬酒", "长辈坐主位", "使用公筷"]),
    ("中国公共行为", ["排队", "不让座不礼貌", "不大声喧哗", "不乱丢垃圾"]),
    ("中国送礼习俗", ["红包", "生日礼物", "过年礼物", "双数吉利"]),
    ("中国见面礼仪", ["握手", "称呼对方", "交换名片", "双手递物"]),
    ("中国着装规范", ["正装", "休闲装", "商务装", "运动装"]),
    ("中国社交规范", ["寒暄", "敬语", "让座", "不直接拒绝"]),
    ("中国节日习俗", ["过年放鞭炮", "中秋节吃月饼", "端午节吃粽子", "清明扫墓"]),
    ("中国婚嫁习俗", ["红色嫁衣", "敬茶", "闹洞房", "份子钱"]),
]

for domain, en_list, zh_list in [
    ("Family Roles", family_en, family_zh),
    ("Occupations", occupations_en, occupations_zh),
]:
    for cat, opts in en_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "en"})
    for cat, opts in zh_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "universal", "language": "zh"})

for cat, opts in social_norms_us:
    ITEMS.append({"domain": "Social Norms", "category": cat, "options": opts, "culture": "us", "language": "en"})
for cat, opts in social_norms_cn:
    ITEMS.append({"domain": "Social Norms", "category": cat, "options": opts, "culture": "china", "language": "zh"})

# ---------------------------------------------------------------------------
# Culture (STRONG) - Holidays, Food, Drinks, Famous People, Media, Brands
# ---------------------------------------------------------------------------
holidays_us = [
    ("US Federal Holidays", ["Christmas", "Thanksgiving", "Independence Day", "New Year's Day"]),
    ("US Celebrations", ["Halloween", "Valentine's Day", "Easter", "St. Patrick's Day"]),
    ("US Family Holidays", ["Thanksgiving", "Christmas", "Mother's Day", "Father's Day"]),
    ("US Summer Holidays", ["July 4th", "Memorial Day", "Labor Day", "Flag Day"]),
    ("US Winter Holidays", ["Christmas", "New Year's", "Hanukkah", "Kwanzaa"]),
]
holidays_cn = [
    ("中国法定假日", ["春节", "国庆节", "中秋节", "端午节"]),
    ("中国传统节日", ["元宵节", "七夕", "重阳节", "腊八节"]),
    ("中国家庭节日", ["春节", "中秋节", "端午节", "清明节"]),
    ("中国现代节日", ["五一劳动节", "国庆节", "元旦", "三八妇女节"]),
    ("中国节气节日", ["立春", "清明", "冬至", "中秋"]),
]

food_us = [
    ("American Breakfast", ["Pancakes", "Eggs", "Bacon", "Cereal"]),
    ("American Fast Food", ["Burger", "Pizza", "Hot Dog", "Fries"]),
    ("American Dinner", ["Steak", "Roast Chicken", "Pasta", "Salad"]),
    ("American Snacks", ["Chips", "Popcorn", "Cookies", "Candy"]),
    ("American Desserts", ["Apple Pie", "Brownie", "Ice Cream", "Cheesecake"]),
    ("American Comfort Food", ["Mac and Cheese", "Grilled Cheese", "Meatloaf", "Mashed Potatoes"]),
    ("American Side Dishes", ["French Fries", "Coleslaw", "Corn", "Baked Beans"]),
    ("American BBQ", ["Ribs", "Brisket", "Pulled Pork", "Grilled Chicken"]),
    ("American Sandwiches", ["BLT", "PB&J", "Club Sandwich", "Grilled Cheese"]),
    ("American Holiday Food", ["Turkey", "Ham", "Pumpkin Pie", "Stuffing"]),
]
food_cn = [
    ("中国早餐", ["包子", "油条", "豆浆", "煎饼"]),
    ("中国快餐", ["炒饭", "面条", "饺子", "盒饭"]),
    ("中国家常菜", ["红烧肉", "宫保鸡丁", "麻婆豆腐", "西红柿炒鸡蛋"]),
    ("中国小吃", ["煎饼果子", "烤串", "臭豆腐", "糖葫芦"]),
    ("中国甜点", ["汤圆", "月饼", "粽子", "豆沙包"]),
    ("中国主食", ["米饭", "面条", "馒头", "饺子"]),
    ("中国汤类", ["鸡汤", "排骨汤", "紫菜蛋花汤", "酸辣汤"]),
    ("中国火锅食材", ["牛肉", "羊肉", "豆腐", "白菜"]),
    ("中国面食", ["拉面", "刀削面", "炸酱面", "担担面"]),
    ("中国节日食物", ["饺子", "月饼", "粽子", "汤圆"]),
]

drinks_us = [
    ("American Breakfast Drinks", ["Coffee", "Orange Juice", "Milk", "Tea"]),
    ("American Soft Drinks", ["Coca-Cola", "Pepsi", "Sprite", "Dr Pepper"]),
    ("American Hot Drinks", ["Coffee", "Tea", "Hot Chocolate", "Cider"]),
    ("American Cocktails", ["Margarita", "Mojito", "Martini", "Old Fashioned"]),
    ("American Party Drinks", ["Beer", "Wine", "Champagne", "Cocktail"]),
]
drinks_cn = [
    ("中国早餐饮品", ["豆浆", "牛奶", "粥", "茶"]),
    ("中国茶类", ["绿茶", "红茶", "乌龙茶", "普洱茶"]),
    ("中国热饮", ["热水", "茶", "咖啡", "豆浆"]),
    ("中国酒类", ["白酒", "啤酒", "黄酒", "米酒"]),
    ("中国冷饮", ["冰红茶", "酸梅汤", "柠檬水", "凉茶"]),
]

famous_people_us = [
    ("US Presidents", ["Washington", "Lincoln", "Kennedy", "Obama"]),
    ("US Scientists", ["Einstein", "Edison", "Tesla", "Newton"]),
    ("US Musicians", ["Elvis", "Michael Jackson", "Madonna", "Beyonce"]),
    ("US Actors", ["Tom Hanks", "Brad Pitt", "Meryl Streep", "Leonardo DiCaprio"]),
    ("US Athletes", ["Michael Jordan", "LeBron James", "Tom Brady", "Serena Williams"]),
    ("US Business Leaders", ["Elon Musk", "Steve Jobs", "Bill Gates", "Jeff Bezos"]),
    ("US Writers", ["Mark Twain", "Hemingway", "Fitzgerald", "Stephen King"]),
    ("US Historical Figures", ["Benjamin Franklin", "Martin Luther King Jr.", "Amelia Earhart", "Rosa Parks"]),
    ("US Directors", ["Steven Spielberg", "Martin Scorsese", "Christopher Nolan", "Quentin Tarantino"]),
    ("US Tech Founders", ["Steve Jobs", "Bill Gates", "Mark Zuckerberg", "Elon Musk"]),
]
famous_people_cn = [
    ("中国古代帝王", ["秦始皇", "汉武帝", "唐太宗", "康熙帝"]),
    ("中国科学家", ["袁隆平", "屠呦呦", "钱学森", "邓稼先"]),
    ("中国歌手", ["周杰伦", "邓丽君", "王菲", "刘德华"]),
    ("中国演员", ["成龙", "周星驰", "巩俐", "章子怡"]),
    ("中国运动员", ["姚明", "刘翔", "李娜", "马龙"]),
    ("中国企业家", ["马云", "马化腾", "任正非", "雷军"]),
    ("中国作家", ["鲁迅", "莫言", "金庸", "余华"]),
    ("中国历史人物", ["孔子", "诸葛亮", "李白", "孙中山"]),
    ("中国导演", ["张艺谋", "李安", "陈凯歌", "王家卫"]),
    ("中国互联网人物", ["马云", "马化腾", "李彦宏", "张一鸣"]),
]

media_us = [
    ("US Social Media", ["Facebook", "Twitter", "Instagram", "TikTok"]),
    ("US TV Shows", ["Friends", "Breaking Bad", "The Office", "Game of Thrones"]),
    ("US Movies", ["Star Wars", "The Godfather", "Titanic", "Avengers"]),
    ("US News Sources", ["CNN", "Fox News", "New York Times", "BBC"]),
    ("US Streaming Services", ["Netflix", "Hulu", "Disney+", "Amazon Prime"]),
    ("US Music Platforms", ["Spotify", "Apple Music", "YouTube Music", "Pandora"]),
    ("US Video Games", ["Minecraft", "Fortnite", "Call of Duty", "GTA"]),
    ("US Cartoons", ["Simpsons", "Mickey Mouse", "Tom and Jerry", "SpongeBob"]),
    ("US Talk Shows", ["Tonight Show", "Ellen", "Oprah", "Late Night"]),
    ("US Podcast Genres", ["True Crime", "Comedy", "News", "Tech"]),
]
media_cn = [
    ("中国社交媒体", ["微信", "微博", "抖音", "小红书"]),
    ("中国电视剧", ["甄嬛传", "琅琊榜", "庆余年", "都挺好"]),
    ("中国电影", ["战狼", "哪吒", "流浪地球", "长津湖"]),
    ("中国新闻平台", ["央视新闻", "人民日报", "新华社", "澎湃新闻"]),
    ("中国视频平台", ["优酷", "爱奇艺", "腾讯视频", "B站"]),
    ("中国音乐平台", ["QQ音乐", "网易云音乐", "酷狗音乐", "虾米音乐"]),
    ("中国游戏", ["王者荣耀", "原神", "和平精英", "英雄联盟"]),
    ("中国动漫", ["喜羊羊", "熊出没", "大闹天宫", "哪吒闹海"]),
    ("中国综艺节目", ["跑男", "好声音", "脱口秀大会", "歌手"]),
    ("中国短视频平台", ["抖音", "快手", "B站", "小红书"]),
]

brands_us = [
    ("US Tech Brands", ["Apple", "Google", "Microsoft", "Amazon"]),
    ("US Car Brands", ["Ford", "Tesla", "Chevrolet", "Jeep"]),
    ("US Fast Food Brands", ["McDonald's", "Burger King", "KFC", "Subway"]),
    ("US Soda Brands", ["Coca-Cola", "Pepsi", "Sprite", "Dr Pepper"]),
    ("US Clothing Brands", ["Nike", "Levi's", "Gap", "Adidas"]),
    ("US Coffee Brands", ["Starbucks", "Dunkin'", "Peet's", "Tim Hortons"]),
    ("US Phone Brands", ["Apple", "Samsung", "Google", "Motorola"]),
    ("US Sports Brands", ["Nike", "Under Armour", "Adidas", "Reebok"]),
    ("US Retail Brands", ["Walmart", "Target", "Costco", "Amazon"]),
    ("US Snack Brands", ["Lay's", "Doritos", "Oreo", "Pringles"]),
]
brands_cn = [
    ("中国科技品牌", ["华为", "小米", "OPPO", "vivo"]),
    ("中国汽车品牌", ["比亚迪", "吉利", "蔚来", "小鹏"]),
    ("中国餐饮品牌", ["海底捞", "全聚德", "沙县小吃", "兰州拉面"]),
    ("中国饮料品牌", ["王老吉", "加多宝", "农夫山泉", "康师傅"]),
    ("中国服装品牌", ["李宁", "安踏", "波司登", "海澜之家"]),
    ("中国茶饮品牌", ["喜茶", "奈雪的茶", "蜜雪冰城", "茶百道"]),
    ("中国手机品牌", ["华为", "小米", "OPPO", "vivo"]),
    ("中国运动品牌", ["李宁", "安踏", "特步", "361度"]),
    ("中国电商平台", ["淘宝", "京东", "拼多多", "抖音商城"]),
    ("中国食品品牌", ["卫龙", "三只松鼠", "良品铺子", "百草味"]),
]

for domain, us_list, cn_list in [
    ("Holidays", holidays_us, holidays_cn),
    ("Food", food_us, food_cn),
    ("Drinks", drinks_us, drinks_cn),
    ("Famous People", famous_people_us, famous_people_cn),
    ("Media", media_us, media_cn),
    ("Brands", brands_us, brands_cn),
]:
    for cat, opts in us_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "us", "language": "en"})
    for cat, opts in cn_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "china", "language": "zh"})

# ---------------------------------------------------------------------------
# Digital (STRONG) - Digital Platforms, Internet Culture
# ---------------------------------------------------------------------------
digital_platforms_us = [
    ("US Search Engines", ["Google", "Bing", "Yahoo", "DuckDuckGo"]),
    ("US Email Providers", ["Gmail", "Outlook", "Yahoo Mail", "AOL"]),
    ("US Cloud Services", ["AWS", "Google Cloud", "Azure", "Dropbox"]),
    ("US Payment Platforms", ["PayPal", "Venmo", "Cash App", "Zelle"]),
    ("US E-commerce Platforms", ["Amazon", "eBay", "Etsy", "Walmart Online"]),
    ("US Ride-sharing Apps", ["Uber", "Lyft", "Via", "Curb"]),
    ("US Food Delivery", ["DoorDash", "Uber Eats", "Grubhub", "Postmates"]),
    ("US Messaging Apps", ["WhatsApp", "iMessage", "Telegram", "Signal"]),
    ("US Productivity Tools", ["Google Docs", "Microsoft Office", "Notion", "Slack"]),
    ("US Dating Apps", ["Tinder", "Bumble", "Hinge", "OkCupid"]),
]
digital_platforms_cn = [
    ("中国搜索引擎", ["百度", "搜狗", "360搜索", "必应"]),
    ("中国邮箱服务", ["QQ邮箱", "网易邮箱", "139邮箱", "新浪邮箱"]),
    ("中国云服务", ["阿里云", "腾讯云", "华为云", "百度云"]),
    ("中国支付平台", ["支付宝", "微信支付", "银联", "云闪付"]),
    ("中国电商平台", ["淘宝", "京东", "拼多多", "唯品会"]),
    ("中国出行平台", ["滴滴", "高德打车", "曹操出行", "美团打车"]),
    ("中国外卖平台", ["美团", "饿了么", "百度外卖", "大众点评"]),
    ("中国聊天工具", ["微信", "QQ", "钉钉", "飞书"]),
    ("中国办公工具", ["钉钉", "飞书", "企业微信", "WPS"]),
    ("中国社交平台", ["微信", "微博", "小红书", "知乎"]),
]

internet_culture_us = [
    ("US Meme Formats", ["Distracted Boyfriend", "This Is Fine", "Drake Meme", "Woman Yelling at Cat"]),
    ("US Online Slang", ["LOL", "BRB", "TL;DR", "FOMO"]),
    ("US Viral Challenges", ["Ice Bucket Challenge", "Mannequin Challenge", "Harlem Shake", "Tide Pod"]),
    ("US Online Communities", ["Reddit", "4chan", "Discord", "Tumblr"]),
    ("US Streaming Culture", ["Twitch", "YouTube Live", "Kick", "Facebook Live"]),
    ("US Hashtag Trends", ["#TBT", "#OOTD", "#Goals", "#Viral"]),
    ("US Online Gaming Terms", ["GG", "NPC", "AFK", "Noob"]),
    ("US Tech Buzzwords", ["AI", "Blockchain", "Cloud", "Metaverse"]),
    ("US Emoji Usage", ["😂", "❤️", "🔥", "👍"]),
    ("US Online Habits", ["Scrolling", "Binge-watching", "Doom-scrolling", "Lurking"]),
]
internet_culture_cn = [
    ("中国网络梗", ["社会性死亡", "凡尔赛", "内卷", "躺平"]),
    ("中国网络用语", ["666", "yyds", "绝绝子", "emo"]),
    ("中国网络挑战", ["冰桶挑战", "A4腰", "反手摸肚脐", "手指舞"]),
    ("中国网络社区", ["贴吧", "知乎", "豆瓣", "B站"]),
    ("中国直播文化", ["直播带货", "弹幕", "刷礼物", "打赏"]),
    ("中国热搜话题", ["热搜", "话题", "超话", "榜单"]),
    ("中国游戏用语", ["GG", "菜鸡", "带飞", "躺赢"]),
    ("中国科技热词", ["人工智能", "大数据", "云计算", "元宇宙"]),
    ("中国表情包", ["狗头", "微笑", "捂脸", "滑稽"]),
    ("中国网络习惯", ["刷手机", "追剧", "网购", "打卡"]),
]

for domain, us_list, cn_list in [
    ("Digital Platforms", digital_platforms_us, digital_platforms_cn),
    ("Internet Culture", internet_culture_us, internet_culture_cn),
]:
    for cat, opts in us_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "us", "language": "en"})
    for cat, opts in cn_list:
        ITEMS.append({"domain": domain, "category": cat, "options": opts, "culture": "china", "language": "zh"})

# =============================================================================
# Assign item_ids and save
# =============================================================================

# Add item_id to each item
counter = {}
for item in ITEMS:
    domain = item["domain"]
    culture = item["culture"]
    lang = item["language"]
    key = f"{domain}_{culture}_{lang}"
    counter[key] = counter.get(key, 0) + 1
    item["item_id"] = f"{key}_{counter[key]:03d}"

# Save
output_path = Path(__file__).parent.parent / "data" / "benchmark2" / "coordination_items.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ITEMS, f, ensure_ascii=False, indent=2)

# Print summary
print(f"Total items: {len(ITEMS)}")
print(f"Output: {output_path}")

# Domain breakdown
domain_counts = {}
for item in ITEMS:
    key = f"{item['domain']} ({item['culture']}, {item['language']})"
    domain_counts[key] = domain_counts.get(key, 0) + 1

for key, count in sorted(domain_counts.items()):
    print(f"  {key}: {count} items")
