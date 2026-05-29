"""
初始化种子数据：电影 + 测试用户 + 模拟评分
运行方式: python seed_data.py
"""
import random
from app import create_app
from models import db, User, Movie, Rating

# 种子电影数据 (30部经典电影)
MOVIES = [
    {"title": "肖申克的救赎", "genres": "剧情|犯罪", "director": "弗兰克·德拉邦特", "actors": "蒂姆·罗宾斯|摩根·弗里曼", "year": 1994, "description": "一个银行家被冤枉入狱，在肖申克监狱中用智慧和毅力寻求自由。"},
    {"title": "霸王别姬", "genres": "剧情|爱情|历史", "director": "陈凯歌", "actors": "张国荣|张丰毅|巩俐", "year": 1993, "description": "两个京剧演员半个世纪的悲欢离合，折射出中国近代史的沧桑巨变。"},
    {"title": "阿甘正传", "genres": "剧情|喜剧|爱情", "director": "罗伯特·泽米吉斯", "actors": "汤姆·汉克斯", "year": 1994, "description": "一个智商只有75的男人，用单纯和善良书写了传奇人生。"},
    {"title": "泰坦尼克号", "genres": "剧情|爱情|灾难", "director": "詹姆斯·卡梅隆", "actors": "莱昂纳多·迪卡普里奥|凯特·温斯莱特", "year": 1997, "description": "一段跨越阶级的爱情故事，在泰坦尼克号沉船事件中永恒。"},
    {"title": "千与千寻", "genres": "动画|奇幻|冒险", "director": "宫崎骏", "actors": "柊瑠美|入野自由", "year": 2001, "description": "少女千寻误入神灵世界，为了拯救变成猪的父母而努力工作。"},
    {"title": "辛德勒的名单", "genres": "剧情|历史|战争", "director": "史蒂文·斯皮尔伯格", "actors": "连姆·尼森", "year": 1993, "description": "二战期间，德国商人辛德勒冒着生命危险拯救了上千名犹太人。"},
    {"title": "盗梦空间", "genres": "科幻|动作|悬疑", "director": "克里斯托弗·诺兰", "actors": "莱昂纳多·迪卡普里奥", "year": 2010, "description": "一个能够进入他人梦境窃取秘密的特工，接受了一项不可能的任务。"},
    {"title": "星际穿越", "genres": "科幻|冒险|剧情", "director": "克里斯托弗·诺兰", "actors": "马修·麦康纳|安妮·海瑟薇", "year": 2014, "description": "一群探险家穿越虫洞，为人类寻找新的家园。"},
    {"title": "这个杀手不太冷", "genres": "剧情|动作|犯罪", "director": "吕克·贝松", "actors": "让·雷诺|娜塔莉·波特曼", "year": 1994, "description": "一个职业杀手与一个小女孩之间不寻常的感情。"},
    {"title": "楚门的世界", "genres": "剧情|科幻|喜剧", "director": "彼得·威尔", "actors": "金·凯瑞", "year": 1998, "description": "一个人发现自己的一生其实是一场真人秀节目。"},
    {"title": "忠犬八公的故事", "genres": "剧情|家庭", "director": "莱塞·霍尔斯道姆", "actors": "理查·基尔", "year": 2009, "description": "一只忠诚的秋田犬每天在车站等待已故主人归来，一等就是十年。"},
    {"title": "海上钢琴师", "genres": "剧情|音乐", "director": "朱塞佩·托纳多雷", "actors": "蒂姆·罗斯", "year": 1998, "description": "一个从未下过船的天才钢琴师，在海上度过传奇一生。"},
    {"title": "三傻大闹宝莱坞", "genres": "剧情|喜剧|爱情", "director": "拉库马·希拉尼", "actors": "阿米尔·汗", "year": 2009, "description": "三个工程系学生用叛逆的方式追求知识和梦想。"},
    {"title": "机器人总动员", "genres": "动画|科幻|爱情", "director": "安德鲁·斯坦顿", "actors": "本·贝尔特", "year": 2008, "description": "在被人类遗弃的地球上，清扫机器人瓦力偶遇探测机器人伊娃。"},
    {"title": "放牛班的春天", "genres": "剧情|音乐", "director": "克里斯托夫·巴拉蒂", "actors": "热拉尔·朱尼奥", "year": 2004, "description": "一位音乐老师用音乐改变了一群问题少年的命运。"},
    {"title": "大话西游之大圣娶亲", "genres": "喜剧|爱情|奇幻", "director": "刘镇伟", "actors": "周星驰|朱茵", "year": 1995, "description": "至尊宝为了救紫霞仙子，戴上紧箍咒变回孙悟空。"},
    {"title": "教父", "genres": "剧情|犯罪", "director": "弗朗西斯·科波拉", "actors": "马龙·白兰度|阿尔·帕西诺", "year": 1972, "description": "一个黑手党家族的权力交接，展现了权力、家庭和忠诚的复杂关系。"},
    {"title": "龙猫", "genres": "动画|家庭|奇幻", "director": "宫崎骏", "actors": "日高法子|�的场光昭", "year": 1988, "description": "两个小女孩在乡下遇到了友善的森林精灵龙猫。"},
    {"title": "当幸福来敲门", "genres": "剧情|传记", "director": "加布里尔·穆奇诺", "actors": "威尔·史密斯", "year": 2006, "description": "一个濒临破产的单亲父亲，通过不懈努力成为股票经纪人。"},
    {"title": "飞屋环游记", "genres": "动画|冒险|喜剧", "director": "彼特·道格特", "actors": "爱德华·阿斯纳", "year": 2009, "description": "一个老人用无数气球带着房子飞往南美洲，实现妻子的遗愿。"},
    {"title": "控方证人", "genres": "剧情|犯罪|悬疑", "director": "比利·怀尔德", "actors": "泰隆·鲍华|玛琳·黛德丽", "year": 1957, "description": "一位病弱的律师为一个被控谋杀的男子辩护，真相出人意料。"},
    {"title": "蝙蝠侠：黑暗骑士", "genres": "剧情|动作|犯罪", "director": "克里斯托弗·诺兰", "actors": "克里斯蒂安·贝尔|希斯·莱杰", "year": 2008, "description": "蝙蝠侠面对最危险的对手小丑，哥谭市陷入混乱。"},
    {"title": "指环王：王者归来", "genres": "奇幻|冒险|剧情", "director": "彼得·杰克逊", "actors": "伊利亚·伍德|维果·莫特森", "year": 2003, "description": "弗罗多和山姆踏上最后的旅程，将魔戒投入末日火山。"},
    {"title": "天堂电影院", "genres": "剧情|爱情", "director": "朱塞佩·托纳多雷", "actors": "菲利普·诺瓦雷", "year": 1988, "description": "一个男孩与电影院放映员之间的忘年之交，以及他成长后对故乡的回忆。"},
    {"title": "搏击俱乐部", "genres": "剧情|悬疑", "director": "大卫·芬奇", "actors": "布拉德·皮特|爱德华·诺顿", "year": 1999, "description": "一个失眠的男人与一个肥皂推销员成立了地下搏击俱乐部。"},
    {"title": "哈利·波特与魔法石", "genres": "奇幻|冒险", "director": "克里斯·哥伦布", "actors": "丹尼尔·雷德克里夫", "year": 2001, "description": "一个孤儿男孩发现自己是巫师，进入霍格沃茨魔法学校学习。"},
    {"title": "少年派的奇幻漂流", "genres": "剧情|奇幻|冒险", "director": "李安", "actors": "苏拉·沙玛", "year": 2012, "description": "一个印度少年与一只孟加拉虎在太平洋上漂流227天。"},
    {"title": "无间道", "genres": "剧情|犯罪|悬疑", "director": "刘伟强|麦兆辉", "actors": "刘德华|梁朝伟", "year": 2002, "description": "警方和黑帮各自安插卧底，两个身份对立的人展开生死较量。"},
    {"title": "摔跤吧！爸爸", "genres": "剧情|传记|运动", "director": "尼特什·提瓦瑞", "actors": "阿米尔·汗", "year": 2016, "description": "一个前摔跤冠军将两个女儿培养成世界级摔跤选手。"},
    {"title": "疯狂动物城", "genres": "动画|冒险|喜剧", "director": "拜伦·霍华德", "actors": "金妮弗·古德温|杰森·贝特曼", "year": 2016, "description": "兔子朱迪和狐狸尼克搭档，揭开动物城的一桩惊天阴谋。"},
]

# 测试用户
TEST_USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "123456"},
    {"username": "bob", "email": "bob@example.com", "password": "123456"},
    {"username": "charlie", "email": "charlie@example.com", "password": "123456"},
    {"username": "diana", "email": "diana@example.com", "password": "123456"},
    {"username": "eve", "email": "eve@example.com", "password": "123456"},
]


def seed():
    app = create_app()
    with app.app_context():
        # 清空数据
        db.session.query(Rating).delete()
        db.session.query(Movie).delete()
        db.session.query(User).delete()
        db.session.commit()

        # 创建用户
        users = []
        for u in TEST_USERS:
            user = User(username=u['username'], email=u['email'])
            user.set_password(u['password'])
            db.session.add(user)
            users.append(user)
        db.session.commit()
        print(f"创建了 {len(users)} 个测试用户")

        # 创建电影
        movies = []
        for m in MOVIES:
            movie = Movie(**m)
            db.session.add(movie)
            movies.append(movie)
        db.session.commit()
        print(f"创建了 {len(movies)} 部电影")

        # 模拟评分 (每个用户随机评 8-15 部电影)
        rating_count = 0
        for user in users:
            num_ratings = random.randint(8, 15)
            rated_movies = random.sample(movies, min(num_ratings, len(movies)))
            for movie in rated_movies:
                # 根据电影评分给一个偏向高分的评分
                base = min(movie.avg_rating if movie.avg_rating > 0 else 3.5, 4.5)
                score = round(random.uniform(max(1, base - 1.5), min(5, base + 0.5)) * 2) / 2
                score = max(1.0, min(5.0, score))

                rating = Rating(
                    user_id=user.id,
                    movie_id=movie.id,
                    score=score
                )
                db.session.add(rating)
                rating_count += 1

                # 更新电影平均分
                total = movie.avg_rating * movie.rating_count + score
                movie.rating_count += 1
                movie.avg_rating = total / movie.rating_count

        db.session.commit()
        print(f"创建了 {rating_count} 条评分记录")
        print("种子数据初始化完成！")


if __name__ == '__main__':
    seed()
