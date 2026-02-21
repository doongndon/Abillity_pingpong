import pygame
import sys
import random
import traceback
import math

# --- 1. 초기화 및 전체 화면 설정 ---
pygame.init()
try:
    pygame.mixer.init()
except:
    pass 

infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
except pygame.error:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("능력자 핑퐁 대전: ULTIMATE")
clock = pygame.time.Clock()

SOUND_PONG = None
SOUND_ABILL = None
SOUND_BUTTON = None 

try:
    SOUND_PONG = pygame.mixer.Sound("pong.mp3")
    SOUND_ABILL = pygame.mixer.Sound("abill.mp3")
    SOUND_BUTTON = pygame.mixer.Sound("butt.mp3") 
    SOUND_PONG.set_volume(0.5)
    SOUND_ABILL.set_volume(0.4)
    SOUND_BUTTON.set_volume(0.6)
except:
    pass

# --- 색상 정의 ---
WHITE = (240, 240, 255); BLACK = (15, 15, 20)
BG_COLOR = (20, 22, 30); PANEL_BG = (35, 38, 50)
ACCENT_COLOR = (100, 200, 255); SEARCH_BG = (50, 55, 70)
MENU_BG = (0, 0, 0, 180); UI_BG = (40, 44, 55)

RED = (255, 80, 80); BLUE = (80, 120, 255); GREEN = (80, 220, 100)
YELLOW = (255, 220, 50); ORANGE = (255, 165, 0); PURPLE = (180, 100, 255)
CYAN = (0, 255, 255); PINK = (255, 130, 180); BROWN = (160, 100, 60)
GOLD = (255, 215, 0); SILVER = (192, 192, 192); LIME = (50, 255, 50)
MAGENTA = (255, 0, 255); TEAL = (0, 128, 128); NAVY = (0, 0, 128)
DARK_GRAY = (60, 60, 60); GRAY = (120, 120, 120); CRIMSON = (220, 20, 60)
MINT = (189, 252, 201); BSOD_BLUE = (0, 0, 170); INDIGO = (75, 0, 130)
THORN_COLOR = (50, 100, 50)

# --- 폰트 설정 ---
def get_font(name, size, bold=False, italic=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold, italic=italic)
    except:
        return pygame.font.SysFont("arial", size, bold=bold, italic=italic)

FONT_MAIN = get_font("malgun gothic", 20)
FONT_TITLE = get_font("malgun gothic", 32, bold=True)
FONT_BIG = get_font("malgun gothic", 80, bold=True)
FONT_DESC = get_font("malgun gothic", 18)
FONT_FLAVOR = get_font("malgun gothic", 16, italic=True)
FONT_UI = get_font("malgun gothic", 14)
FONT_PARTICLE = get_font("segoe ui emoji", 24)
FONT_EFFECT = get_font("malgun gothic", 24, bold=True)
FONT_HUD = get_font("malgun gothic", 16, bold=True)

# --- 2. 데이터 클래스 ---

class AbilityData:
    def __init__(self, name, flavor, desc, color):
        self.name = name
        self.flavor = flavor
        self.desc = desc
        self.color = color
        lines = desc.split('\n')
        self.q_name = "스킬"
        self.sp_name = "궁극기"
        for line in lines:
            if line.startswith("[Q]"): self.q_name = line.replace("[Q]", "").strip()
            if line.startswith("[Sp]"): self.sp_name = line.replace("[Sp]", "").strip()

ABILITIES = {
    0: AbilityData("화염 정령", "다 태워버리겠어!", "공에 불이 붙어 닿으면 화상을 입음\n[Q] 파이어 볼\n[Sp] 인페르노", RED),
    1: AbilityData("얼음 여왕", "얼어붙어라.", "상대 진영에 얼음 블록을 생성해 방해\n[Q] 빙벽 생성\n[Sp] 절대영도", CYAN),
    2: AbilityData("바람의 신", "바람처럼 빠르게.", "공이 예측 불가능한 곡선으로 휨\n[Q] 돌풍\n[Sp] 허리케인 샷", (150, 255, 200)),
    3: AbilityData("거인", "지나갈 수 없다.", "패들이 화면 절반을 덮을 만큼 커짐\n[Q] 거대화\n[Sp] 진격의 거인", (150, 100, 50)),
    4: AbilityData("시간 술사", "시간을 지배한다.", "공을 멈췄다가 초고속으로 가속\n[Q] 타임 스톱\n[Sp] 크로노 브레이크", PURPLE),
    5: AbilityData("도박사", "인생은 한 방!", "잭팟(초가속) 또는 파산(기력0)\n[Q] 동전 던지기\n[Sp] 러시안 룰렛", GOLD),
    6: AbilityData("뱀파이어", "피가 필요해...", "상대의 기력을 뺏어 내 것으로 만듦\n[Q] 흡혈\n[Sp] 블러드 피스트", (150, 0, 0)),
    7: AbilityData("닌자", "그림자 숨기.", "공이 중간에서 사라졌다가 나타남\n[Q] 연막술\n[Sp] 암습", DARK_GRAY),
    8: AbilityData("저격수", "한 발이면 돼.", "상하 움직임 없는 초고속 직사포\n[Q] 록온\n[Sp] 헤드샷", (50, 50, 50)),
    9: AbilityData("치유사", "치료해드릴게요.", "팀 전체의 크기와 기력을 회복\n[Q] 힐링\n[Sp] 대천사의 포옹", GREEN),
    10: AbilityData("해커", "시스템 해킹 중...", "상대 조작키 반전 및 에러 블록 생성\n[Q] 키보드 해킹\n[Sp] 방화벽 설치", LIME),
    11: AbilityData("네크로맨서", "일어나라.", "죽어도 한 번 즉시 부활\n[Q] 영혼 수확\n[Sp] 리치 왕의 계약", (50, 0, 50)),
    12: AbilityData("자석 인간", "찌릿찌릿할 걸?", "공이 내 패들 쪽으로 휘어짐\n[Q] 인력\n[Sp] 자기장 폭풍", MAGENTA),
    13: AbilityData("건축가", "통곡의 벽.", "경기장 중앙에 물리적 벽 설치\n[Q] 바리케이드\n[Sp] 철의 장막", BROWN),
    14: AbilityData("광전사", "크아아아!!", "체력이 낮을수록 공이 빨라짐\n[Q] 분노\n[Sp] 불사신 모드", (200, 50, 50)),
    15: AbilityData("환술사", "이게 진짜일까?", "가짜 공을 소환하여 혼란 유발\n[Q] 분신\n[Sp] 미러 이미지", PINK),
    16: AbilityData("중력 술사", "무릎 꿇어라.", "공이 바닥으로 뚝 떨어지게 만듦\n[Q] 그라비티\n[Sp] 이벤트 호라이즌", NAVY),
    17: AbilityData("반사 전문가", "반사!", "어떤 공이든 자동으로 막아냄\n[Q] 오토 가드\n[Sp] 절대 반사", WHITE),
    18: AbilityData("독술사", "서서히 죽어가리라.", "공에 독을 발라 닿으면 중독시킴\n[Q] 독침\n[Sp] 맹독 확산", (100, 255, 100)),
    19: AbilityData("복사술사", "네 기술 쩔더라?", "상대의 스킬을 뺏어서 사용\n[Q] 카피캣\n[Sp] 도플갱어", (200, 200, 200)),
    20: AbilityData("해적 선장", "전탄 발사!", "대포알처럼 무거운 공 발사\n[Q] 럼주통\n[Sp] 캐논 볼", (139, 0, 0)),
    21: AbilityData("사이보그", "목표 조준.", "완벽한 각도로 계산된 반사\n[Q] 궤적 연산\n[Sp] 터미네이트", TEAL),
    22: AbilityData("슬라임", "물렁물렁~", "공이 닿으면 끈적하게 붙었다 발사\n[Q] 점액 발사\n[Sp] 킹 슬라임", (0, 255, 0)),
    23: AbilityData("경찰", "꼼짝 마라!", "상대 진영에 바리케이드 설치\n[Q] 불심검문\n[Sp] 통행 금지", BLUE),
    24: AbilityData("복싱 챔피언", "원 투!", "공을 강하게 밀쳐내며 가속\n[Q] 잽\n[Sp] 핵펀치", (255, 140, 0)),
    25: AbilityData("외계인", "지구 정복.", "공을 랜덤 위치로 포털 이동\n[Q] 웜홀\n[Sp] 차원 도약", (0, 255, 127)),
    26: AbilityData("테니스 선수", "15 Love!", "휘어지는 드라이브 샷\n[Q] 슬라이스\n[Sp] 트위스트 서브", (255, 255, 100)),
    27: AbilityData("과학자", "실험 시작.", "공 크기를 아주 작거나 크게 만듦\n[Q] 축소 광선\n[Sp] 거대화 광선", (128, 0, 128)),
    28: AbilityData("아이돌", "내 눈을 바라봐.", "상대 진영 전체를 하트 커튼으로 가림\n[Q] 윙크\n[Sp] 팬미팅", (255, 192, 203)),
    29: AbilityData("요리사", "주문 받습니다!", "공이 프라이팬 볶듯이 튐\n[Q] 웍질\n[Sp] 불쇼", (210, 105, 30)),
    30: AbilityData("무도가", "아도겐!", "장풍으로 원거리에서 공을 쳐냄\n[Q] 파동권\n[Sp] 진공파동권", YELLOW),
    31: AbilityData("드루이드", "자연의 힘으로.", "상대 진영에 나무를 심어 방해\n[Q] 덩굴 손\n[Sp] 숲의 장벽", (34, 139, 34)),
    32: AbilityData("마술사", "사라져라 얍!", "공이 사라졌다가 골대 앞에서 나타남\n[Q] 배니싱\n[Sp] 일루전", (100, 0, 100)),
    33: AbilityData("광대", "히히히!", "풍선 장애물을 마구 소환\n[Q] 저글링\n[Sp] 서커스 천막", (255, 0, 255)),
    34: AbilityData("대장장이", "망치 맛 좀 봐라.", "공이 무쇠처럼 무거워짐 (중력 강화)\n[Q] 담금질\n[Sp] 헤비 메탈", (100, 100, 100)),
    35: AbilityData("전기 기술자", "100만 볼트!", "공에 닿으면 감전되어 잠시 마비\n[Q] 스파크\n[Sp] 썬더 볼트", (255, 255, 0)),
    36: AbilityData("식물학자", "무럭무럭 자라라.", "공이 닿으면 작은 공으로 분열\n[Q] 씨앗 뿌리기\n[Sp] 과잉 성장", (0, 128, 0)),
    37: AbilityData("카우보이", "석양이 진다..", "가장 빠른 탄속의 총알 슛\n[Q] 패닝\n[Sp] 황야의 무법자", (210, 180, 140)),
    38: AbilityData("사무라이", "베지 못할 건 없다.", "공을 베어 순간적으로 가속\n[Q] 발도\n[Sp] 일섬", (220, 20, 60)),
    39: AbilityData("폭파 전문가", "폭발은 예술이야.", "공이 닿으면 폭발하며 상대를 밀쳐냄\n[Q] C4\n[Sp] 메가톤 폭발", (50, 50, 50)),
    40: AbilityData("유령", "우우우...", "공이 상대 패들을 통과할 확률 부여\n[Q] 폴터가이스트\n[Sp] 유체이탈", (200, 200, 255)),
    41: AbilityData("용기사", "용의 힘이여!", "용의 형상으로 공이 굽이침\n[Q] 드래곤 테일\n[Sp] 드래곤 브레스", (139, 0, 0)),
    42: AbilityData("기상캐스터", "강풍 주의보입니다.", "강한 바람으로 공을 위아래로 밈\n[Q] 강풍\n[Sp] 태풍의 눈", (135, 206, 235)),
    43: AbilityData("판사", "유죄!", "상대 패들을 아주 작게 만듦\n[Q] 구속\n[Sp] 사형 선고", WHITE),
    44: AbilityData("낚시꾼", "월척이다!", "공을 내 쪽으로 강제로 당겨옴\n[Q] 낚아채기\n[Sp] 만선의 꿈", (0, 191, 255)),
    45: AbilityData("미식축구", "터치다운!", "패들이 돌진하여 공을 강타\n[Q] 태클\n[Sp] 슈퍼볼", (165, 42, 42)),
    46: AbilityData("고고학자", "저주받은 유물...", "상대 진영을 고대 석판으로 막음\n[Q] 유물 발굴\n[Sp] 파라오의 저주", (210, 180, 140)),
    47: AbilityData("조련사", "앉아!", "공이 멈추라고 하면 멈춤\n[Q] 기다려\n[Sp] 물어!", (205, 133, 63)),
    48: AbilityData("바리스타", "뜨거워요.", "상대 진영 전체를 커피 얼룩으로 덮음\n[Q] 원두 투척\n[Sp] 에스프레소 샤워", (101, 67, 33)),
    49: AbilityData("지휘관", "돌격 앞으로!", "작은 병사(공)들 소환\n[Q] 지원 사격\n[Sp] 전군 돌격", (0, 0, 139)),
    50: AbilityData("서퍼", "파도 좋고!", "파도타듯 꿀렁이는 공\n[Q] 서핑\n[Sp] 빅 웨이브", CYAN),
    51: AbilityData("화가", "예술이야.", "화면을 페인트로 덧칠해 가림\n[Q] 페인트\n[Sp] 캔버스 덮기", YELLOW),
    52: AbilityData("우주인", "무중력 상태.", "중력이 사라져 공이 둥둥 뜸\n[Q] 무중력\n[Sp] 블랙홀 생성", SILVER),
    53: AbilityData("락스타", "Make some noise!", "음파로 공을 진동시킴\n[Q] 샤우팅\n[Sp] 데스 메탈", PURPLE),
    54: AbilityData("스파이", "은밀하게.", "공이 투명해짐\n[Q] 은폐\n[Sp] 공작 활동", BLACK),
    55: AbilityData("바이킹", "발할라!", "패들이 매우 빨라지고 공격적\n[Q] 약탈\n[Sp] 버서커 모드", BROWN),
    56: AbilityData("안드로이드", "계산 완료.", "공의 궤적을 미리 보여줌\n[Q] 궤적 분석\n[Sp] 오토 에임", TEAL),
    57: AbilityData("숲의 요정", "숲을 지켜줘.", "상대를 덩굴로 묶음\n[Q] 구속의 씨앗\n[Sp] 세계수의 뿌리", GREEN),
    58: AbilityData("연금술사", "등가교환.", "공을 금덩이(매우 무거움)로 변환\n[Q] 골드 러시\n[Sp] 현자의 돌", GOLD),
    59: AbilityData("늑대인간", "아우우우!", "일정 시간동안 속도/파워 대폭 상승\n[Q] 야성\n[Sp] 블러드 러스트", DARK_GRAY),
    60: AbilityData("헌터", "잡았다.", "상대 코트에 덫 설치\n[Q] 곰 덫\n[Sp] 사냥 개시", CRIMSON),
    61: AbilityData("저승사자", "갈 시간이다.", "상대 기력을 0으로 만듦\n[Q] 데스 사이드\n[Sp] 영혼 수거", (20, 20, 80)),
    62: AbilityData("투우사", "올레!", "공이 휘어져서 옴\n[Q] 붉은 천\n[Sp] 투우의 춤", RED),
    63: AbilityData("광인", "히히히히!", "랜덤 방향으로 공 튐\n[Q] 혼돈\n[Sp] 조커 박스", PINK),
    64: AbilityData("발레리나", "우아하게.", "우아한 곡선 슛\n[Q] 피루엣\n[Sp] 백조의 호수", WHITE),
    65: AbilityData("스님", "관세음보살.", "공의 속도를 초기화(느리게)\n[Q] 평정심\n[Sp] 금강불괴", ORANGE),
    66: AbilityData("CEO", "얼마면 돼?", "상대 기력을 빼앗아 내 기력을 채움 (뇌물)\n[Q] 뇌물\n[Sp] 적대적 인수", GOLD),
    67: AbilityData("크래커", "다 뚫어주지.", "게임 화면에 글리치 효과\n[Q] 버그 생성\n[Sp] 블루스크린", GREEN),
    68: AbilityData("시간여행자", "미래에서 왔다.", "공을 과거 위치로 되감음\n[Q] 리와인드\n[Sp] 타임 패러독스", CYAN),
    69: AbilityData("개발자", "버그 아닙니다.", "공이 텔레포트하거나 멈춤\n[Q] 긴급 점검\n[Sp] 밸런스 붕괴", BLUE),
    70: AbilityData("수학쌤", "이건 시험에 나온다.", "공이 사인 그래프(물결)로 옴\n[Q] 삼각함수\n[Sp] 미적분 공격", WHITE),
    71: AbilityData("교통경찰", "신호 위반!", "공을 강제로 멈춤\n[Q] 정지 신호\n[Sp] 면허 취소", BLUE),
    72: AbilityData("게이머", "아 렉걸려;", "공이 뚝뚝 끊기며 이동(렉)\n[Q] 핑 튀김\n[Sp] 랜선 뽑기", LIME),
    73: AbilityData("유튜버", "구독 좋아요!", "좋아요 블록으로 상대 진영 전체 도배\n[Q] 어그로\n[Sp] 실버 버튼", RED),
    74: AbilityData("건물주", "월세 내세요.", "중앙에 물리적 벽을 세움\n[Q] 입주\n[Sp] 알박기", GOLD),
    75: AbilityData("미용사", "손님 이건 고데기예요", "공의 스타일(속도/궤적) 변경\n[Q] 커트\n[Sp] 매직 스트레이트", PINK),
    76: AbilityData("배달원", "배달 왔습니다!", "공이 가속하다 감속함\n[Q] 급가속\n[Sp] 총알 배송", MINT),
    77: AbilityData("정원사", "가지치기합니다.", "가시 덤불(공 파괴/멈춤) 생성\n[Q] 덤불 설치\n[Sp] 가시 지옥", GREEN),
    78: AbilityData("소방관", "불이야!", "물대포로 공을 밀어냄\n[Q] 방수\n[Sp] 고압 살수", RED),
    79: AbilityData("파일럿", "이륙합니다.", "공이 비행기처럼 솟구침\n[Q] 이륙\n[Sp] 음속 돌파", SILVER),
    80: AbilityData("광부", "금이다!", "돌덩이(장애물) 투척\n[Q] 채굴\n[Sp] 다이너마이트", GOLD),
    81: AbilityData("사육사", "밥 먹자~", "공이 동물처럼 제멋대로 움직임\n[Q] 간식\n[Sp] 야생의 부름", ORANGE),
    82: AbilityData("점술가", "운명이 보여요.", "공이 닿을 곳을 미리 표시\n[Q] 타로\n[Sp] 미래 예지", PURPLE),
    83: AbilityData("기자", "특종입니다!", "신문지로 상대 화면 전체를 덮어버림\n[Q] 셔터\n[Sp] 호외요 호외", WHITE),
    84: AbilityData("탐정", "범인은 너!", "가짜 공 중 진짜를 찾아라\n[Q] 추리\n[Sp] 범인 지목", BROWN),
    85: AbilityData("보디가드", "VIP 보호.", "패들 앞에 방패 생성\n[Q] 경호\n[Sp] 철통 보안", BLACK),
    86: AbilityData("외교관", "대화로 합시다.", "공 속도를 아주 느리게 만듬\n[Q] 협상\n[Sp] 평화 조약", BLUE),
    87: AbilityData("해녀", "숨 참아!", "물방울(방해물) 생성\n[Q] 물질\n[Sp] 심해의 공포", CYAN),
    88: AbilityData("양궁 선수", "텐! 텐! 텐!", "바람의 영향을 받지 않는 직사\n[Q] 조준\n[Sp] 퍼펙트 골드", YELLOW),
    89: AbilityData("축구 선수", "골~~~!", "공이 바나나킥처럼 휨\n[Q] 감아차기\n[Sp] 무회전 슛", WHITE),
    90: AbilityData("농부", "풍년이로세.", "공이 여러개로 늘어남\n[Q] 파종\n[Sp] 대풍년", GREEN),
    91: AbilityData("패션모델", "멋지게 한 컷.", "워킹하듯 지그재그 이동\n[Q] 런웨이\n[Sp] 피날레", PINK),
    92: AbilityData("타짜", "동작 그만.", "공을 바꿔치기(위치이동)\n[Q] 밑장빼기\n[Sp] 사쿠라네?", RED),
    93: AbilityData("래퍼", "Drop the Beat.", "박자에 맞춰 공 속도 변화\n[Q] 플로우\n[Sp] 쇼미더머니", BLACK),
    94: AbilityData("감독", "레디~ 액션!", "슬레이트 치면 공이 멈춤\n[Q] 컷!\n[Sp] 크랭크 인", WHITE),
    95: AbilityData("좀비", "크아아...", "패들이 느려지지만 안죽음(부활)\n[Q] 감염\n[Sp] 좀비 아포칼립스", GREEN),
    96: AbilityData("천사", "축복을.", "패들 크기 증가 + 회복\n[Q] 가호\n[Sp] 디바인 프로텍션", GOLD),
    97: AbilityData("악마", "계약할래?", "상대 진영을 암흑 장막으로 완전히 가림\n[Q] 암흑\n[Sp] 지옥의 불길", RED),
    98: AbilityData("투명인간", "안 보이지?", "공과 패들이 투명해짐\n[Q] 투명화\n[Sp] 완전 은폐", GRAY),
    99: AbilityData("더 히어로", "정의의 이름으로!", "모든 능력치가 조금씩 상승\n[Q] 각성\n[Sp] 필살기", BLUE),
    100: AbilityData("치과의사", "아~ 하세요.", "드릴 소리와 함께 진동(공포)\n[Q] 신경 치료\n[Sp] 발치", WHITE),
    101: AbilityData("네일아티스트", "블링블링하게!", "공이 화려하게 빛남(눈부심)\n[Q] 큐빅\n[Sp] 젤 네일 아트", PINK),
    102: AbilityData("최면술사", "레드 썬!", "상대 조작키가 계속 바뀜\n[Q] 혼란\n[Sp] 집단 최면", PURPLE),
    103: AbilityData("바텐더", "한 잔 받으시죠.", "공이 취한듯 비틀거림\n[Q] 셰이킹\n[Sp] 독한 칵테일", ORANGE),
    104: AbilityData("서커스 단장", "쇼타임!", "장애물과 가짜 공 소환\n[Q] 묘기\n[Sp] 그랜드 쇼", RED),
    105: AbilityData("고양이", "야옹.", "공을 툭툭 침 (궤적 변경)\n[Q] 냥냥펀치\n[Sp] 츄르 내놔", YELLOW),
    106: AbilityData("강아지", "멍멍!", "공을 쫓아다님 (유도탄)\n[Q] 물어와\n[Sp] 산책 시간", BROWN),
    107: AbilityData("청소기", "먼지 제거.", "공을 빨아들여 멈춤\n[Q] 흡입\n[Sp] 터보 모드", SILVER),
    108: AbilityData("포병", "좌표 확인.", "공이 포물선을 그리며 낙하\n[Q] 곡사포\n[Sp] 융단 폭격", GREEN),
    109: AbilityData("태양", "태양 만세!", "주변을 태워버림(기력감소)\n[Q] 일광욕\n[Sp] 솔라 빔", ORANGE),
    110: AbilityData("달", "차오른다...", "중력을 낮춰 공을 띄움\n[Q] 만유인력\n[Sp] 풀 문", YELLOW),
    111: AbilityData("별", "반짝반짝.", "작은 별똥별(탄막) 발사\n[Q] 스타폴\n[Sp] 갤럭시", CYAN),
    112: AbilityData("구름", "몽글몽글.", "상대 진영을 구름으로 가림\n[Q] 안개\n[Sp] 먹구름", WHITE),
    113: AbilityData("비", "주륵주륵.", "비가 내려 공이 미끄러짐\n[Q] 소나기\n[Sp] 장마철", BLUE),
    114: AbilityData("눈", "펑펑.", "상대를 얼려 움직임을 둔화\n[Q] 눈덩이\n[Sp] 블리자드", WHITE),
    115: AbilityData("안개", "앞이 안 보여.", "경기장 중앙이 안보임\n[Q] 연막\n[Sp] 사일런트 힐", GRAY),
    116: AbilityData("무지개", "빨주노초파남보.", "공 색깔이 계속 변함\n[Q] 굴절\n[Sp] 오버 더 레인보우", MAGENTA),
    117: AbilityData("오로라", "아름답지?", "아름다운 궤적으로 시선 분산\n[Q] 극광\n[Sp] 노던 라이트", GREEN),
    118: AbilityData("네크로댄서", "춤춰라!", "강제로 점프/이동 시킴\n[Q] 비트\n[Sp] 댄스 플로어", PURPLE),
    119: AbilityData("차원 관리자", "균형을 수호한다.", "공이 화면 끝에서 반대로 나옴\n[Q] 포탈\n[Sp] 차원 붕괴", BLACK),
    120: AbilityData("드론 조종사", "타겟 록온.", "공을 원격 조종(유도)\n[Q] 호버링\n[Sp] 공습 경보", TEAL),
    121: AbilityData("ASMR 아티스트", "쉿...", "공이 아주 느리게 이동\n[Q] 탭핑\n[Sp] 이어 클리닝", PINK),
    122: AbilityData("민트초코", "호불호 끝판왕.", "공이 호/불호(밀거나 당김)\n[Q] 치약맛\n[Sp] 민초의 난", MINT),
    123: AbilityData("헬창", "근손실 온다.", "공이 무겁지만 빠름\n[Q] 프로틴\n[Sp] 3대 500", BROWN),
    124: AbilityData("K-POP 스타", "센터는 나야.", "화려한 조명과 음표 발사\n[Q] 엔딩 요정\n[Sp] 월드 투어", PURPLE),
    125: AbilityData("편의점 알바", "봉투 필요하세요?", "바코드 찍듯 공 정지\n[Q] 폐기 도시락\n[Sp] 진상 손님", ORANGE),
    126: AbilityData("주식 트레이더", "가즈아!", "공이 주가처럼 떡상/떡락\n[Q] 매수\n[Sp] 상장 폐지", RED),
    127: AbilityData("렉카", "어디 사고 났나?", "공을 강제로 끌고 감\n[Q] 견인\n[Sp] 사이버 렉카", YELLOW),
    128: AbilityData("키보드 워리어", "타닥타닥...", "글자 탄막 발사\n[Q] 악플\n[Sp] 신상 털기", BLACK),
    129: AbilityData("고인물", "나 때는 말이야.", "최소한의 움직임으로 방어\n[Q] 훈수\n[Sp] 썩은 물", DARK_GRAY),
    130: AbilityData("뉴비", "어떻게 해요?", "예측 불가능한 움직임\n[Q] 질문\n[Sp] 트롤링", LIME),
    131: AbilityData("슬라임 킹", "합체!", "공이 분열되었다 합체\n[Q] 증식\n[Sp] 킹 슬라임", GREEN),
    132: AbilityData("골렘", "단단하다.", "거대한 바위 장애물\n[Q] 짱돌\n[Sp] 지진", GRAY),
    133: AbilityData("그림자 군주", "일어나라...", "검은 잔상이 남음\n[Q] 그림자\n[Sp] 그림자 군단", BLACK),
    134: AbilityData("빛의 수호자", "빛이여!", "상대 진영을 하얀 빛으로 완전히 가림\n[Q] 플래시\n[Sp] 태양권", GOLD),
    135: AbilityData("타임 키퍼", "시간은 금.", "라운드를 강제로 리셋함\n[Q] 째깍째깍\n[Sp] 타임 루프", SILVER),
    136: AbilityData("공간 절단자", "싹둑.", "공간을 잘라 공 이동\n[Q] 웜홀\n[Sp] 차원 절단", NAVY),
    137: AbilityData("마리오네트", "춤춰라 인형아.", "상대를 실로 조종\n[Q] 꼭두각시\n[Sp] 인형극", CRIMSON),
    138: AbilityData("리치", "죽음은 시작일 뿐.", "부활 및 상대 체력 흡수\n[Q] 라이프 베슬\n[Sp] 필라테리", PURPLE),
    139: AbilityData("성기사", "신성한 방패.", "무적 방패 생성\n[Q] 디바인 실드\n[Sp] 신의 심판", GOLD),
    140: AbilityData("바드", "노래해요~", "음표가 날아다님(방해)\n[Q] 불협화음\n[Sp] 힐링 송", PINK),
    141: AbilityData("도적", "뒤를 조심해.", "공이 패들 뒤에서 나타남\n[Q] 백스탭\n[Sp] 암살", BLACK),
    142: AbilityData("수도승", "아미타불.", "장풍으로 공을 쳐냄\n[Q] 철사장\n[Sp] 여래신장", ORANGE),
    143: AbilityData("레인저", "백발백중.", "화살(빠른 공) 연사\n[Q] 속사\n[Sp] 애로우 레인", GREEN),
    144: AbilityData("흑마법사", "영혼을 바쳐라.", "도트 데미지(기력)\n[Q] 부패\n[Sp] 파멸의 의식", PURPLE),
    145: AbilityData("정령사", "정령의 분노.", "랜덤 원소 효과 발동\n[Q] 소환\n[Sp] 정령왕", CYAN),
    146: AbilityData("AI 챗봇", "무엇을 도와드릴까요?", "답변 생성중...(렉 유발)\n[Q] 토큰 생성\n[Sp] 할루시네이션", TEAL),
    147: AbilityData("예언자", "다 보인다.", "공의 경로를 점선으로 미리 표시\n[Q] 예지\n[Sp] 미래 확정", WHITE),
    148: AbilityData("데몬 헌터", "악마 사냥.", "쌍권총 난사\n[Q] 구르기\n[Sp] 악마의 형상", DARK_GRAY),
    149: AbilityData("갓파더", "거절할 수 없는 제안.", "상대를 잠시 얼어붙게 만드는 공포\n[Q] 거래\n[Sp] 패밀리", BLACK),
    150: AbilityData("도자기 장인", "조심조심...", "공이 닿으면 파편이 튐(장애물)\n[Q] 빚기\n[Sp] 가마 굽기", BROWN),
    151: AbilityData("서예가", "일필휘지.", "상대 진영을 먹물로 완전히 덮음\n[Q] 붓질\n[Sp] 수묵화", BLACK),
    152: AbilityData("고무인간", "쭉쭉 늘어나라!", "패들이 아주 길어짐\n[Q] 스트레칭\n[Sp] 기어 서드", PINK),
    153: AbilityData("사이버 트럭", "단단하다.", "절대 부서지지 않는 벽돌 같은 공\n[Q] 방탄\n[Sp] 풀 악셀", SILVER),
    154: AbilityData("양자 물리학자", "관측 전까진 모른다.", "공이 두 개로 보임(중첩)\n[Q] 슈뢰딩거\n[Sp] 양자 도약", TEAL),
    155: AbilityData("드라큘라", "피... 더 많은 피...", "흡혈 강화 버전\n[Q] 흡혈 박쥐\n[Sp] 피의 축제", CRIMSON),
    156: AbilityData("성직자", "빛이 너를 태우리라.", "공을 칠 때마다 정화(가속)\n[Q] 축복\n[Sp] 성스러운 빛", GOLD),
    157: AbilityData("대장군", "화살비!", "하늘에서 화살이 쏟아짐(장애물)\n[Q] 사격 명령\n[Sp] 일제 사격", BROWN),
    158: AbilityData("폭풍의 눈", "중심으로.", "공을 화면 중앙으로 강하게 당김\n[Q] 인력\n[Sp] 토네이도", NAVY),
    159: AbilityData("마그마", "바닥이 용암이야!", "중앙 영역에 닿으면 기력 감소\n[Q] 분화\n[Sp] 화산 폭발", RED),
    160: AbilityData("빙산", "타이타닉도 침몰했지.", "거대한 얼음벽 생성\n[Q] 빙벽\n[Sp] 빙하기", CYAN),
    161: AbilityData("모래시계", "시간은 흐른다.", "공 속도가 서서히 빨라짐\n[Q] 모래바람\n[Sp] 시간 가속", GOLD),
    162: AbilityData("거울", "반사.", "공을 반사하는 거울 벽 설치\n[Q] 거울상\n[Sp] 미러 룸", SILVER),
    163: AbilityData("그림자", "나를 따르라.", "공 뒤에 그림자 공이 따라다님\n[Q] 쉐도우\n[Sp] 그림자 분신", DARK_GRAY),
    164: AbilityData("역병 의사", "치료제는 없다.", "공에 닿으면 패들이 병듦(속도감소)\n[Q] 전염\n[Sp] 흑사병", PURPLE),
    165: AbilityData("글리치", "010101...", "화면이 깨지고 공이 순간이동\n[Q] 노이즈\n[Sp] 치명적 오류", GREEN),
    166: AbilityData("행운아", "오늘 운 좋은데?", "랜덤한 긍정 효과 발동\n[Q] 럭키 세븐\n[Sp] 로또 당첨", YELLOW),
    167: AbilityData("불운아", "왜 나만...", "랜덤한 부정 효과를 상대에게 줌\n[Q] 머피의 법칙\n[Sp] 액운", GRAY),
    168: AbilityData("초신성", "별의 죽음.", "공이 폭발하며 주변을 밀어냄\n[Q] 팽창\n[Sp] 빅뱅", ORANGE),
    169: AbilityData("창조주", "빛이 있으라.", "랜덤한 블록과 아이템 생성\n[Q] 창조\n[Sp] 제네시스", WHITE),
    170: AbilityData("테트리스 마스터", "줄을 맞춰라.", "하늘에서 블록이 떨어짐(장애물)\n[Q] 블록 낙하\n[Sp] 라인 클리어", (200, 50, 200)),
    171: AbilityData("그라피티 아티스트", "낙서 시작!", "상대 진영을 페인트로 완전히 덮음\n[Q] 스프레이\n[Sp] 스트리트 아트", (100, 255, 100)),
    172: AbilityData("양봉업자", "꿀맛 좀 볼래?", "끈적한 벌집 장벽 설치\n[Q] 꿀벌 소환\n[Sp] 로열 젤리", (255, 200, 0)),
    173: AbilityData("교통정리", "우회하세요.", "라바콘(장애물) 설치\n[Q] 진입 금지\n[Sp] 도로 통제", (255, 100, 0)),
    174: AbilityData("도서관 사서", "조용히 하세요.", "책장으로 벽을 쌓음\n[Q] 책장 정리\n[Sp] 지식의 탑", (139, 69, 19)),
    175: AbilityData("라면 요리사", "면치기 한 판?", "꼬불꼬불한 면발 장애물\n[Q] 육수\n[Sp] 차슈 추가", (255, 255, 150)),
    176: AbilityData("기상 관측관", "비가 오겠네요.", "먹구름으로 상대 진영 완전 차단\n[Q] 소나기\n[Sp] 폭풍 전야", (100, 100, 150)),
    177: AbilityData("대장장이(각성)", "더 뜨겁게!", "뜨거운 모루가 떨어짐(장애물)\n[Q] 망치질\n[Sp] 전설의 검", (80, 80, 80)),
    178: AbilityData("뱀파이어 헌터", "악을 멸한다.", "십자가 장애물 설치\n[Q] 은화살\n[Sp] 성수 투척", (200, 200, 255)),
    179: AbilityData("국왕", "짐이 곧 국가다.", "성벽을 쌓아 방어\n[Q] 성벽 건설\n[Sp] 근위대 소집", (255, 215, 0)),
    180: AbilityData("무대 감독", "커튼 콜!", "상대 진영에 암전 커튼(완전 가림)\n[Q] 조명 끄기\n[Sp] 블랙아웃", BLACK),
    181: AbilityData("대왕 오징어", "먹물 발사!", "화면 전체를 먹물로 덮어버림\n[Q] 먹물\n[Sp] 크라켄", (50, 0, 50)),
    182: AbilityData("샌드맨", "좋은 꿈 꿔.", "모래 폭풍으로 화면을 가리고 재움\n[Q] 수면 가루\n[Sp] 악몽", (237, 201, 175)),
    183: AbilityData("심해 잠수부", "빛이 닿지 않는 곳.", "심해의 어둠으로 화면 차단\n[Q] 잠수\n[Sp] 심해 공포", (0, 0, 50)),
    184: AbilityData("메두사", "내 눈을 봐.", "상대를 석화(멈춤)시키고 돌로 시야 차단\n[Q] 석화 광선\n[Sp] 고르곤의 눈", (100, 100, 100)),
    185: AbilityData("좀비 군단장", "뇌... 내놔...", "좀비 떼가 화면을 뒤덮음\n[Q] 바이러스\n[Sp] 호드", (50, 100, 50)),
    186: AbilityData("불꽃놀이 장인", "펑! 펑!", "화려한 불꽃으로 시야를 마비시킴\n[Q] 폭죽\n[Sp] 피날레", (255, 100, 100)),
    187: AbilityData("스모그", "콜록콜록.", "매캐한 연기로 화면 전체 가림\n[Q] 매연\n[Sp] 독가스", (100, 100, 100)),
    188: AbilityData("종이술사", "종이접기.", "종이가 날려 화면을 가림\n[Q] 종이 비행기\n[Sp] 천 개의 종이학", WHITE),
    189: AbilityData("블랙홀", "모든 것을 삼킨다.", "빛조차 빠져나갈 수 없는 어둠(가림)\n[Q] 중력 붕괴\n[Sp] 특이점", BLACK),
    200: AbilityData("체인저", "자리를 바꿔볼까?", "상대와 패들 위치를 맞바꿈\n[Q] 스위치\n[Sp] 공간 전이", MAGENTA),
    201: AbilityData("마인 레이어", "발 밑을 조심해.", "상대 필드에 투명 지뢰 설치\n[Q] 매설\n[Sp] 연쇄 폭발", DARK_GRAY),
    202: AbilityData("도플갱어", "둘이면 천하무적.", "나를 돕는 AI 패들 소환\n[Q] 분신 소환\n[Sp] 듀오 모드", WHITE),
    203: AbilityData("타임 로드", "시간이여 멈춰라.", "나를 제외한 모든 것을 정지(더 월드)\n[Q] 스톱\n[Sp] 더 월드", GOLD),
    204: AbilityData("슈링커", "작아져라!", "상대 패들을 일시적으로 축소\n[Q] 축소빔\n[Sp] 마이크로 사이즈", TEAL),
    205: AbilityData("그라비티 웰", "빨려들어간다!", "중앙에 공을 빨아들이는 블랙홀 생성\n[Q] 싱귤래리티\n[Sp] 사건의 지평선", PURPLE),
    206: AbilityData("팩맨", "맵은 둥글다.", "공이 화면 밖으로 나가면 반대편에서 나옴\n[Q] 워프\n[Sp] 무한 루프", YELLOW),
    207: AbilityData("뱀파이어 로드", "네 힘은 나의 것.", "상대 패들 크기를 뺏어옴\n[Q] 사이즈 스틸\n[Sp] 흡수", CRIMSON),
    208: AbilityData("리코셰", "각도 계산 완료.", "공이 벽에 닿을수록 빨라짐\n[Q] 도탄\n[Sp] 핀볼 모드", ORANGE),
    209: AbilityData("아키텍트", "미로는 복잡할수록 좋지.", "움직이는 미로 벽 생성\n[Q] 설계\n[Sp] 미궁", BROWN),
}

MAX_SCORE = 10
MAX_STAMINA = 100
COST_BASIC = 10
COST_SKILL = 30
COST_ULT = 100
TEAM_1 = 1
TEAM_2 = 2

# --- 3. 이펙트 시스템 ---

class ScreenShake:
    def __init__(self):
        self.duration = 0; self.magnitude = 0
    def start(self, duration, magnitude):
        self.duration = duration; self.magnitude = magnitude
        if SOUND_ABILL: SOUND_ABILL.play()
    def get_offset(self):
        if self.duration > 0:
            self.duration -= 1
            return random.randint(-self.magnitude, self.magnitude), random.randint(-self.magnitude, self.magnitude)
        return 0, 0

shake_effect = ScreenShake()

class Particle:
    def __init__(self, x, y, color, speed=3, size=8, symbol=None, p_type="EXPLODE"):
        self.x = x; self.y = y; self.color = color; self.size = size
        self.symbol = symbol; self.life = 255; self.p_type = p_type
        self.gravity = 0; self.decay = 4; self.vx = 0; self.vy = 0
        self.angle = random.uniform(0, 6.28); self.rotation_speed = random.uniform(-0.2, 0.2)
        
        if p_type in ["EXPLODE", "STAR", "PIXEL", "SHARD", "HEART", "BOLT", "GLITCH", "RAINBOW", "SMILE"]:
            angle = random.uniform(0, 2 * math.pi); spd = random.uniform(1, speed)
            self.vx = math.cos(angle) * spd; self.vy = math.sin(angle) * spd
        elif p_type in ["RISE", "NOTE", "BUBBLE", "FIRE", "POISON"]:
            self.vx = random.uniform(-1, 1); self.vy = random.uniform(-speed, -1); self.gravity = -0.02
        elif p_type in ["FALL", "SNOW", "MONEY", "INK"]:
            self.vx = random.uniform(-1, 1); self.vy = random.uniform(1, speed); self.gravity = 0.05
        elif p_type == "BEAM":
            self.vx = speed; self.vy = random.uniform(-0.5, 0.5); self.decay = 15
        elif p_type == "SHOCKWAVE":
            self.size = 1; self.decay = 8
        elif p_type == "SPIRAL":
            self.angle = random.uniform(0, 6.28); self.radius = 1
        elif p_type == "IMPLODE":
            angle = random.uniform(0, 2 * math.pi); dist = random.uniform(50, 100)
            self.target_x = x; self.target_y = y
            self.x = x + math.cos(angle) * dist; self.y = y + math.sin(angle) * dist
            self.vx = (self.target_x - self.x) * 0.05; self.vy = (self.target_y - self.y) * 0.05
            self.decay = 6
        elif p_type in ["TRAIL", "SOLID_TRAIL"]:
            self.decay = 15

    def update(self):
        if self.p_type == "SHOCKWAVE": self.size += 5; self.life -= self.decay
        elif self.p_type == "SPIRAL":
            self.angle += 0.2; self.radius += 2
            self.x += math.cos(self.angle) * 2; self.y += math.sin(self.angle) * 2
            self.life -= self.decay
        else:
            self.x += self.vx; self.y += self.vy; self.vy += self.gravity
            self.life -= self.decay; self.angle += self.rotation_speed
            if self.p_type not in ["BEAM", "SHOCKWAVE", "TEXT", "FIRE", "POISON", "SOLID_TRAIL"]:
                self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life <= 0: return
        alpha_color = (*self.color, int(self.life))
        if self.p_type == "SHOCKWAVE":
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, alpha_color, (int(self.size), int(self.size)), int(self.size), width=3)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        elif self.symbol:
            try: text_surf = FONT_PARTICLE.render(self.symbol, True, self.color)
            except: text_surf = FONT_UI.render(self.symbol, True, self.color)
            text_surf.set_alpha(int(self.life)); surface.blit(text_surf, (int(self.x), int(self.y)))
        elif self.p_type == "STAR":
            points = []
            for i in range(5):
                angle = self.angle + i * (2 * math.pi / 5) - math.pi / 2
                points.append((self.x + math.cos(angle) * self.size, self.y + math.sin(angle) * self.size))
                angle += (2 * math.pi / 5) / 2
                points.append((self.x + math.cos(angle) * (self.size/2), self.y + math.sin(angle) * (self.size/2)))
            if len(points) > 2: pygame.draw.polygon(surface, self.color, points)
        elif self.p_type == "RAINBOW":
            c = random.choice([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE])
            pygame.draw.circle(surface, c, (int(self.x), int(self.y)), int(self.size))
        elif self.p_type == "INK":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size * 1.5))
        elif self.p_type == "HEART":
            x, y, s = self.x, self.y, self.size
            pygame.draw.circle(surface, self.color, (int(x - s/2), int(y - s/2)), int(s/2))
            pygame.draw.circle(surface, self.color, (int(x + s/2), int(y - s/2)), int(s/2))
            points = [(x - s, y - s/4), (x + s, y - s/4), (x, y + s)]
            pygame.draw.polygon(surface, self.color, points)
        elif self.p_type == "BOLT":
            points = []; lx, ly = self.x, self.y
            for _ in range(3):
                points.append((lx, ly)); lx += random.randint(-5, 5) + self.vx; ly += random.randint(5, 10) + self.vy
            if len(points) > 1: pygame.draw.lines(surface, self.color, False, points, 2)
        elif self.p_type == "GLITCH":
            w = random.randint(5, 20); h = random.randint(2, 5)
            pygame.draw.rect(surface, self.color, (self.x, self.y, w, h))
        elif self.p_type == "FIRE":
            fire_color = (min(255, self.color[0] + 50), max(0, self.color[1] - 20), 0)
            pygame.draw.circle(surface, fire_color, (int(self.x), int(self.y)), int(self.size))
        elif self.p_type == "POISON":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
            pygame.draw.circle(surface, (100, 255, 100), (int(self.x), int(self.y)), int(self.size/2))
        elif self.p_type in ["PIXEL", "SOLID_TRAIL"]:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))
        elif self.p_type == "NOTE":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
            pygame.draw.line(surface, self.color, (int(self.x+self.size), int(self.y)), (int(self.x+self.size), int(self.y-self.size*2)), 2)
        else:
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, alpha_color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x), int(self.y)))

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x; self.y = y; self.text = text; self.color = color
        self.life = 60; self.y_offset = 0
    def update(self): self.y_offset -= 1; self.life -= 1
    def draw(self, surface):
        if self.life > 0:
            text_surf = FONT_EFFECT.render(self.text, True, self.color)
            text_surf.set_alpha(min(255, self.life * 5))
            surface.blit(text_surf, (self.x - text_surf.get_width()//2, self.y + self.y_offset))

class CenterEffect:
    def __init__(self, text, color):
        self.text = text; self.color = color; self.life = 90; self.scale = 1.0
    def update(self):
        self.life -= 1
        if self.life > 70: self.scale += 0.05
        elif self.life < 20: self.scale -= 0.05
    def draw(self, surface):
        if self.life > 0 and self.scale > 0:
            base_surf = FONT_BIG.render(self.text, True, self.color)
            w = int(base_surf.get_width() * self.scale); h = int(base_surf.get_height() * self.scale)
            if w > 0 and h > 0:
                scaled_surf = pygame.transform.scale(base_surf, (w, h))
                rect = scaled_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                shadow = pygame.transform.scale(FONT_BIG.render(self.text, True, BLACK), (w, h))
                shadow.set_alpha(150)
                surface.blit(shadow, (rect.x+5, rect.y+5))
                surface.blit(scaled_surf, rect)

particles = []; floating_texts = []; obstacles = []; central_effects = []; fake_balls = []

# ─── 환경 이벤트 시스템 ───────────────────────────────────────────────
field_event = None
field_event_timer = 0
field_event_announce = 0
next_event_time = 0
FIELD_EVENT_INTERVAL = 18000
FIELD_EVENT_DURATION = 7000

FIELD_EVENTS = [
    ('quake',     '지진 발생!',    RED,    '경기장이 흔들린다!'),
    ('flood',     '홍수!',         BLUE,   '바닥이 물에 잠겼다! 중력 증가!'),
    ('blackout',  '정전!',         (30,30,30), '아무것도 안 보인다!'),
    ('windstorm', '폭풍!',         CYAN,   '공이 강한 바람에 휩쓸린다!'),
    ('heatwave',  '폭염!',         ORANGE, '기력이 빠르게 소진된다!'),
    ('timewarp',  '시간 왜곡!',    PURPLE, '공의 속도가 뒤틀린다!'),
    ('mirrorfield','거울 필드!',   SILVER, '모든 조작이 반전된다!'),
]

# 상태이상 아이콘 (타이머 키 -> (텍스트, 색상))
STATUS_ICONS = {
    'frozen':      ('ICE',   CYAN),
    'stunned':     ('ZAP',   YELLOW),
    'poison':      ('PSN',   (100,255,100)),
    'burn':        ('BRN',   ORANGE),
    'reversed':    ('REV',   LIME),
    'confused':    ('CNF',   PINK),
    'infected':    ('INF',   PURPLE),
    'shrunk':      ('SML',   TEAL),
    'giant':       ('BIG',   GREEN),
    'speed_boost': ('SPD',   GOLD),
    'auto_defend': ('DEF',   WHITE),
    'revive':      ('REV',   (150,0,150)),
}

def spawn_particles(x, y, color, count=10, speed=3, size=6, symbol=None, p_type="EXPLODE"):
    if len(particles) > 500: count = max(1, count // 2)
    for _ in range(count): particles.append(Particle(x, y, color, speed, size, symbol, p_type))

def spawn_text(x, y, text, color): floating_texts.append(FloatingText(x, y, text, color))

def spawn_center_effect(text, color):
    central_effects.append(CenterEffect(text, color)); shake_effect.start(15, 5)

def spawn_blind_obstacles(target_paddle, color, count=15, full_cover=False):
    is_left_side = target_paddle.rect.centerx < SCREEN_WIDTH // 2
    min_x = 0 if is_left_side else SCREEN_WIDTH // 2
    max_x = SCREEN_WIDTH // 2 if is_left_side else SCREEN_WIDTH
    if full_cover:
        obstacles.append(Obstacle(min_x, 0, max_x - min_x, SCREEN_HEIGHT, 3000, "BLIND", color=color))
    else:
        for _ in range(count):
            w = random.randint(30, 80); h = random.randint(30, 80)
            x = random.randint(min_x, max_x - w); y = random.randint(0, SCREEN_HEIGHT - h)
            obstacles.append(Obstacle(x, y, w, h, 3000, "BLIND", color=color))

def draw_trajectory(surface, ball):
    sim_x, sim_y = ball.rect.x, ball.rect.y
    sim_vx, sim_vy = ball.speed_x, ball.speed_y
    points = [(sim_x + 10, sim_y + 10)]
    for _ in range(15):
        sim_x += sim_vx * 3; sim_y += sim_vy * 3
        if sim_y <= 0 or sim_y >= SCREEN_HEIGHT - 20: sim_vy *= -1
        points.append((sim_x + 10, sim_y + 10))
    if len(points) > 1:
        pygame.draw.lines(surface, (100, 200, 255), False, points, 2)
        pygame.draw.circle(surface, WHITE, (int(points[-1][0]), int(points[-1][1])), 4)

# ─── 환경 이벤트 시스템 함수들 ──────────────────────────────────────────

def trigger_field_event():
    """랜덤 환경 이벤트 발동"""
    global field_event, field_event_timer, field_event_announce, next_event_time
    ev = random.choice(FIELD_EVENTS)
    field_event = ev[0]
    now = pygame.time.get_ticks()
    field_event_timer = now + FIELD_EVENT_DURATION
    field_event_announce = now + 3000
    next_event_time = now + FIELD_EVENT_INTERVAL + random.randint(-3000, 3000)
    # 이벤트 안내 텍스트
    spawn_center_effect(ev[1], ev[2])
    spawn_text(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80, ev[3], ev[2])

def end_field_event():
    """환경 이벤트 종료 처리"""
    global field_event
    field_event = None

def update_field_event(ball_ref):
    """매 프레임 환경 이벤트 효과 적용"""
    global field_event, field_event_timer, next_event_time
    now = pygame.time.get_ticks()

    # 이벤트 종료 체크
    if field_event and now > field_event_timer:
        end_field_event()
        spawn_text(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '이벤트 종료', GRAY)

    # 다음 이벤트 발동
    if field_event is None and next_event_time > 0 and now > next_event_time:
        trigger_field_event()

    if field_event is None: return

    # 이벤트별 지속 효과
    if field_event == 'quake':
        # 매 프레임 랜덤 흔들기 + 가끔 바위 장애물
        if random.random() < 0.04:
            shake_effect.magnitude = max(shake_effect.magnitude, 6)
            shake_effect.duration = max(shake_effect.duration, 8)
        if random.random() < 0.015:
            obstacles.append(Obstacle(
                random.randint(200, SCREEN_WIDTH-200),
                random.randint(100, SCREEN_HEIGHT-200),
                random.randint(20,50), random.randint(20,50),
                2000, "WALL", color=GRAY))

    elif field_event == 'flood':
        # 공에 추가 중력 부여
        ball_ref.gravity_scale = max(ball_ref.gravity_scale, 0.4)
        # 하단 물 파티클
        if random.random() < 0.08:
            spawn_particles(random.randint(0,SCREEN_WIDTH), SCREEN_HEIGHT-20,
                          BLUE, count=2, speed=2, size=4, p_type="RISE")

    elif field_event == 'blackout':
        pass  # draw에서 처리 (화면 오버레이)

    elif field_event == 'windstorm':
        # 공에 랜덤 Y 방향 힘 부여
        wind = math.sin(now * 0.003) * 6
        ball_ref.extra_vel_y += wind
        if random.random() < 0.06:
            spawn_particles(random.randint(0, SCREEN_WIDTH),
                          random.randint(0, SCREEN_HEIGHT),
                          CYAN, count=2, speed=5, size=3, p_type="BEAM")

    elif field_event == 'heatwave':
        # 모든 패들 기력 서서히 감소
        for p in paddles:
            p.stamina = max(0, p.stamina - 0.15)
        # 화염 파티클
        if random.random() < 0.05:
            spawn_particles(random.randint(0, SCREEN_WIDTH),
                          random.randint(0, SCREEN_HEIGHT),
                          ORANGE, count=2, size=4, p_type="FIRE")

    elif field_event == 'timewarp':
        # 공 속도를 진동시킴
        warp = math.sin(now * 0.005) * 3
        ball_ref.speed_x += warp * (0.05 if ball_ref.speed_x > 0 else -0.05)

    elif field_event == 'mirrorfield':
        pass  # 패들 이동 처리는 move_manual에서 체크

def draw_field_event_overlay(surface):
    """환경 이벤트 시각 오버레이"""
    if field_event is None: return
    now = pygame.time.get_ticks()

    if field_event == 'blackout':
        # 매우 어두운 오버레이 (패들/공 아주 희미하게)
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 210))
        surface.blit(dark, (0, 0))

    elif field_event == 'flood':
        # 하단 1/4 물 오버레이
        water = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT//4), pygame.SRCALPHA)
        water.fill((0, 80, 200, 80))
        surface.blit(water, (0, SCREEN_HEIGHT*3//4))
        # 물결선
        for i in range(0, SCREEN_WIDTH, 30):
            wave_y = SCREEN_HEIGHT*3//4 + int(math.sin(now*0.003 + i*0.1) * 6)
            pygame.draw.circle(surface, (100, 180, 255), (i, wave_y), 3)

    elif field_event == 'heatwave':
        # 빨간 흐림 오버레이
        heat = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(30 + math.sin(now * 0.004) * 20)
        heat.fill((200, 80, 0, alpha))
        surface.blit(heat, (0, 0))

    elif field_event == 'windstorm':
        # 가로선 바람 효과
        for i in range(0, SCREEN_HEIGHT, 40):
            offset = int(math.sin(now * 0.005 + i) * 20)
            alpha = 60
            s = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
            s.fill((100, 220, 255, alpha))
            surface.blit(s, (offset, i))

    elif field_event == 'timewarp':
        # 보라 + 격자 왜곡 오버레이
        warp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, 60):
            for y in range(0, SCREEN_HEIGHT, 60):
                wx = x + int(math.sin(now*0.003 + y*0.02) * 8)
                wy = y + int(math.cos(now*0.003 + x*0.02) * 8)
                pygame.draw.circle(warp_surf, (180, 80, 255, 40), (wx, wy), 3)
        surface.blit(warp_surf, (0,0))

    elif field_event == 'mirrorfield':
        # 좌우 미러 표시
        mirror = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        mirror.fill((192, 192, 192, 25))
        surface.blit(mirror, (0,0))
        # 중앙 거울 선
        for y in range(0, SCREEN_HEIGHT, 8):
            pygame.draw.line(surface, (200,200,255), (SCREEN_WIDTH//2, y), (SCREEN_WIDTH//2, y+4), 2)

    # 이벤트 잔여 시간 표시
    remain = max(0, field_event_timer - now)
    ev_name = next((e[1] for e in FIELD_EVENTS if e[0] == field_event), "이벤트")
    ev_color = next((e[2] for e in FIELD_EVENTS if e[0] == field_event), WHITE)
    bar_w = 300
    ratio = remain / FIELD_EVENT_DURATION
    bar_x = SCREEN_WIDTH//2 - bar_w//2
    bar_y = SCREEN_HEIGHT - 30
    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_w, 10), border_radius=5)
    pygame.draw.rect(surface, ev_color, (bar_x, bar_y, int(bar_w * ratio), 10), border_radius=5)
    ev_txt = FONT_UI.render(f"★ {ev_name} ({remain//1000+1}s)", True, ev_color)
    surface.blit(ev_txt, (SCREEN_WIDTH//2 - ev_txt.get_width()//2, bar_y - 18))

def split_ball(ball_ref, count=2):
    """공을 count개로 분열 (가짜 공 생성)"""
    for i in range(count):
        fb = Ball(is_fake=True)
        fb.rect.center = ball_ref.rect.center
        angle = (2 * math.pi / count) * i
        spd = abs(ball_ref.speed_x) * random.uniform(0.8, 1.2)
        fb.speed_x = math.cos(angle) * spd
        fb.speed_y = math.sin(angle) * spd
        fb.color = ball_ref.color
        fake_balls.append(fb)

def draw_status_icons(surface, paddle, is_left):
    """패들 위에 상태이상 아이콘을 작은 뱃지로 표시"""
    now = pygame.time.get_ticks()
    active = [(label, color) for key, (label, color) in STATUS_ICONS.items()
              if paddle.timers.get(key, 0) > now]
    if not active: return

    icon_w, icon_h = 36, 20
    gap = 4
    total_w = len(active) * (icon_w + gap)
    start_x = paddle.rect.centerx - total_w // 2
    start_y = paddle.rect.top - 28

    for i, (label, color) in enumerate(active):
        ix = start_x + i * (icon_w + gap)
        # 뱃지 배경
        badge = pygame.Surface((icon_w, icon_h), pygame.SRCALPHA)
        badge.fill((*color, 180))
        surface.blit(badge, (ix, start_y))
        pygame.draw.rect(surface, color, (ix, start_y, icon_w, icon_h), 1, border_radius=3)
        # 텍스트
        t = FONT_UI.render(label, True, BLACK)
        surface.blit(t, (ix + icon_w//2 - t.get_width()//2, start_y + icon_h//2 - t.get_height()//2))

# --- 4. 게임 객체 ---

class Obstacle:
    def __init__(self, x, y, w, h, duration, o_type="WALL", color=None, team=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.spawn_time = pygame.time.get_ticks(); self.duration = duration
        self.o_type = o_type; self.team = team
        if color: self.color = color
        elif o_type == "THORN": self.color = THORN_COLOR
        elif o_type == "PORTAL": self.color = PURPLE
        elif o_type == "ICE": self.color = CYAN
        elif o_type == "MIRROR": self.color = SILVER
        elif o_type == "BUMPER": self.color = GOLD
        elif o_type == "MINE": self.color = DARK_GRAY
        else: self.color = BROWN

    def is_expired(self): return pygame.time.get_ticks() - self.spawn_time > self.duration

    def draw(self, surface):
        if self.o_type == "BLIND":
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill((*self.color, 230)); surface.blit(s, (self.rect.x, self.rect.y)); return
        if self.o_type == "THORN":
            pygame.draw.rect(surface, self.color, self.rect)
            for i in range(0, self.rect.width, 10):
                pygame.draw.polygon(surface, LIME, [(self.rect.left+i, self.rect.top), (self.rect.left+i+5, self.rect.top-10), (self.rect.left+i+10, self.rect.top)])
        elif self.o_type == "PORTAL":
            pygame.draw.ellipse(surface, self.color, self.rect)
            pygame.draw.ellipse(surface, WHITE, self.rect, 3)
        elif self.o_type == "ICE":
            pygame.draw.rect(surface, (200, 240, 255), self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)
        elif self.o_type == "MIRROR":
            pygame.draw.rect(surface, SILVER, self.rect)
            pygame.draw.line(surface, WHITE, self.rect.topleft, self.rect.bottomright, 2)
        elif self.o_type == "BUMPER":
            pygame.draw.ellipse(surface, GOLD, self.rect)
            pygame.draw.ellipse(surface, RED, self.rect, 4)
        elif self.o_type == "MINE":
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.circle(s, (50, 50, 50, 100), (self.rect.width//2, self.rect.height//2), self.rect.width//2)
            surface.blit(s, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

class Paddle:
    def __init__(self, x, y, is_ai=False, team=TEAM_1, duration=None):
        self.team = team; self.is_ai = is_ai; self.duration = duration
        self.spawn_time = pygame.time.get_ticks() if duration else 0
        self.original_height = 60 if game_mode == "2VS2" else 100
        self.rect = pygame.Rect(x, y, 20, self.original_height)
        self.color = WHITE; self.base_speed = 8; self.current_speed = 8
        self.stamina = 100.0; self.stamina_regen = 0.12
        self.ability_id = -1; self.difficulty_level = 1
        self.ai_reaction_timer = 0; self.ai_target_y = y
        self.ai_error_offset = 0; self.ai_ability_cooldown = 0
        # --- 쿨다운 추적 (UI 표시용) ---
        self.last_skill_used = 0
        self.last_ult_used = 0
        self.skill_cooldown_ms = 3000
        self.ult_cooldown_ms = 8000
        self.timers = {
            'frozen':0,'reversed':0,'giant':0,'speed_boost':0,
            'revive':0,'auto_defend':0,'poison':0,'blind':0,
            'stunned':0,'shrunk':0,'invisible':0,'drunk':0,
            'burn':0,'confused':0,'infected':0
        }

    def is_expired(self):
        if self.duration is None: return False
        return pygame.time.get_ticks() - self.spawn_time > self.duration

    def apply_effect(self, effect_name, duration_ms): self.timers[effect_name] = pygame.time.get_ticks() + duration_ms

    def check_durations(self):
        now = pygame.time.get_ticks()
        target_h = self.original_height
        if now < self.timers['giant']: target_h = self.original_height * 2.5
        elif now < self.timers['shrunk']: target_h = self.original_height * 0.4
        if self.rect.height != int(target_h):
            old_center = self.rect.center; self.rect.height = int(target_h)
            self.rect.center = old_center; self.rect.clamp_ip(screen.get_rect())
        if now > self.timers['speed_boost']: self.current_speed = self.base_speed
        else: self.current_speed = self.base_speed * 1.6
        if now < self.timers['poison'] and random.random() < 0.1:
            self.stamina = max(0, self.stamina - 0.8)
            spawn_particles(self.rect.centerx, self.rect.centery, GREEN, 1, 2, symbol="☠", p_type="POISON")
        if now < self.timers['burn'] and random.random() < 0.15:
            self.stamina = max(0, self.stamina - 1.5)
            spawn_particles(self.rect.centerx, self.rect.centery, RED, 1, 2, p_type="FIRE")
        if now < self.timers['infected'] and random.random() < 0.1:
            self.current_speed = self.base_speed * 0.5
            spawn_particles(self.rect.centerx, self.rect.centery, PURPLE, 1, 1, p_type="PIXEL")

    def update(self, ball_ref):
        self.check_durations(); now = pygame.time.get_ticks()
        if now < self.timers['stunned'] or now < self.timers['frozen']:
            sym = "❄" if now < self.timers['frozen'] else "⚡"
            color = CYAN if now < self.timers['frozen'] else YELLOW
            if random.random() < 0.1: spawn_particles(self.rect.centerx, self.rect.centery, color, 1, 2, symbol=sym, p_type="RISE")
            return
        regen_mult = 1.5 if (self.is_ai and self.difficulty_level == 3) else 1.0
        if self.stamina < MAX_STAMINA and not (now < self.timers['poison'] or now < self.timers['burn']):
            self.stamina += self.stamina_regen * regen_mult
        if now < self.timers['auto_defend']:
            self.ai_move(ball_ref, force_perfect=True)
            spawn_particles(self.rect.centerx, self.rect.centery, WHITE, 1, 2, p_type="RISE"); return
        if self.is_ai: self.ai_move(ball_ref)

    def move_manual(self, up, down):
        now = pygame.time.get_ticks()
        if now < self.timers['stunned'] or now < self.timers['frozen']: return
        is_reversed = (now < self.timers['reversed'])
        # 환경 이벤트: 거울 필드 → 모든 조작 반전
        if field_event == 'mirrorfield':
            is_reversed = not is_reversed
        if now < self.timers['confused']:
            if random.random() < 0.1: is_reversed = not is_reversed
            if random.random() < 0.3: up, down = down, up
        if now < self.timers['drunk'] and random.random() < 0.2: up = not up; down = not down
        if is_reversed: up, down = down, up
        if up and self.rect.top > 0: self.rect.y -= self.current_speed
        if down and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.current_speed

    def ai_move(self, ball_ref, force_perfect=False):
        now = pygame.time.get_ticks()
        reaction_delay_base = [400, 250, 120, 0]
        error_range = [80, 45, 15, 0]
        skill_chance_ult = [0.001, 0.008, 0.02, 0.05]
        skill_chance_skill = [0.005, 0.02, 0.05, 0.1]
        level = self.difficulty_level
        if now < self.timers['stunned'] or now < self.timers['frozen']: return
        is_confused = (now < self.timers['blind']) or (ball_ref.timers['invisible'] > now)
        if is_confused:
            if random.random() < 0.05: self.ai_target_y = random.randint(0, SCREEN_HEIGHT)
        elif now > self.ai_reaction_timer or force_perfect or level == 3:
            base_delay = reaction_delay_base[level]
            self.ai_reaction_timer = now + base_delay + random.randint(-30, 30)
            if force_perfect or level == 3: self.ai_error_offset = 0
            else:
                curve_factor = random.randint(-50, 50) if ball_ref.extra_vel_y != 0 and level < 2 else 0
                self.ai_error_offset = random.randint(-error_range[level], error_range[level]) + curve_factor
            self.ai_target_y = ball_ref.rect.centery + self.ai_error_offset
        move_spd = self.current_speed * (1.3 if level == 3 else 1.0)
        if now < self.timers['reversed']: move_spd *= -1
        if self.rect.centery < self.ai_target_y: self.rect.y += min(abs(move_spd), self.ai_target_y - self.rect.centery) * (1 if move_spd>0 else -1)
        elif self.rect.centery > self.ai_target_y: self.rect.y -= min(abs(move_spd), self.rect.centery - self.ai_target_y) * (1 if move_spd>0 else -1)
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
        if not force_perfect and is_confused: return
        if self.is_ai and now > self.ai_ability_cooldown:
            dist_x = abs(self.rect.centerx - ball_ref.rect.centerx)
            is_incoming = (ball_ref.speed_x > 0) if self.team == TEAM_2 else (ball_ref.speed_x < 0)
            if is_incoming and dist_x < 500:
                used = False
                if self.stamina >= 100 and random.random() < skill_chance_ult[level]:
                    if use_ability(self, "ULT", ball_ref): used = True
                elif self.stamina >= 30 and random.random() < skill_chance_skill[level]:
                    if use_ability(self, "SKILL", ball_ref): used = True
                if used:
                    cooldown_base = [8000, 5000, 3000, 1000]
                    self.ai_ability_cooldown = now + random.randint(cooldown_base[level]//2, cooldown_base[level])

    def draw(self, surface):
        if pygame.time.get_ticks() < self.timers['invisible']:
            if random.random() > 0.1: return
        if self.duration and (self.spawn_time + self.duration - pygame.time.get_ticks() < 2000):
            if (pygame.time.get_ticks() // 200) % 2 == 0: return
        draw_color = self.color
        now = pygame.time.get_ticks()
        if now < self.timers['frozen']: draw_color = CYAN
        elif now < self.timers['stunned']: draw_color = YELLOW
        elif now < self.timers['poison']: draw_color = GREEN
        elif now < self.timers['burn']: draw_color = ORANGE
        elif now < self.timers['reversed']: draw_color = LIME
        elif now < self.timers['infected']: draw_color = PURPLE
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=8)
        bar_width = self.rect.width * 4; bar_x = self.rect.centerx - bar_width // 2; bar_y = self.rect.bottom + 10
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, 6), border_radius=3)
        current_width = max(0, min(int((self.stamina / MAX_STAMINA) * bar_width), bar_width))
        stamina_color = ACCENT_COLOR if self.stamina >= 100 else GREEN
        if self.stamina < 30: stamina_color = RED
        pygame.draw.rect(surface, stamina_color, (bar_x, bar_y, current_width, 6), border_radius=3)
        label = "P" if not self.is_ai else "AI"
        l_surf = FONT_UI.render(label, True, BLACK)
        surface.blit(l_surf, (self.rect.centerx - l_surf.get_width()//2, self.rect.y + 5))
        # 상태이상 아이콘
        draw_status_icons(surface, self, self.rect.centerx < SCREEN_WIDTH // 2)

class Ball:
    def __init__(self, is_fake=False):
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - 10, SCREEN_HEIGHT//2 - 10, 20, 20)
        self.base_speed_x = 9; self.speed_x = 9; self.speed_y = 9
        self.color = WHITE; self.visible = True; self.is_fake = is_fake
        self.extra_vel_y = 0; self.gravity_scale = 0; self.is_ghost = False
        self.wrap_around = False; self.last_hit_team = 0
        self.timers = {
            'invisible':0,'magnet':0,'gravity':0,'gravity_flip':0,
            'fake':0,'sticky':0,'wave':0,'wrap':0,'lag':0,'wobble':0,
            'stop':0,'fire':0,'flash':0,'poison':0,'shock':0,'ink':0,'guide':0
        }
        self.magnet_target = None; self.sticky_target = None; self.portal_cooldown = 0
        # 리코셰 벽 반사 카운트
        self.bounce_count = 0

    def reset(self, direction):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = self.base_speed_x * direction
        self.speed_y = random.choice([-7, -6, 6, 7])
        self.color = WHITE; self.visible = True; self.is_fake = False
        self.extra_vel_y = 0; self.gravity_scale = 0; self.is_ghost = False
        self.wrap_around = False; self.last_hit_team = 0; self.bounce_count = 0
        for k in self.timers: self.timers[k] = 0
        self.sticky_target = None; self.portal_cooldown = 0

    def apply_effect(self, effect_name, duration_ms): self.timers[effect_name] = pygame.time.get_ticks() + duration_ms

    def update_effects(self):
        now = pygame.time.get_ticks()
        if now < self.timers['stop']: return True
        if now < self.timers['lag']:
            if (now // 100) % 2 == 0: return True
        if now > self.timers['invisible']: self.visible = True
        else: self.visible = False
        if now < self.timers['flash']:
            self.speed_y = 0; self.extra_vel_y = 0
            spawn_particles(self.rect.centerx, self.rect.centery, self.color, 2, 0, p_type="PIXEL")
        if now < self.timers['magnet'] and self.magnet_target:
            target_y = self.magnet_target.rect.centery
            if self.rect.centery < target_y: self.speed_y += 0.7
            else: self.speed_y -= 0.7
            spawn_particles(self.rect.centerx, self.rect.centery, MAGENTA, 1, 2, symbol="U")
        if now < self.timers['gravity_flip']:
            self.gravity_scale = -0.8
            spawn_particles(self.rect.centerx, self.rect.centery, PURPLE, 2, 2, p_type="IMPLODE")
        elif now < self.timers['gravity']:
            center_y = SCREEN_HEIGHT // 2
            if self.rect.centery < center_y: self.speed_y += 0.9
            else: self.speed_y -= 0.9
            spawn_particles(self.rect.centerx, self.rect.centery, NAVY, 2, 2, p_type="IMPLODE")
        else: self.gravity_scale = 0
        self.wrap_around = (now < self.timers['wrap'])
        self.extra_vel_y = 0
        if now < self.timers['wave']: self.extra_vel_y = math.sin(now * 0.015) * 15
        if now < self.timers['wobble']: self.extra_vel_y = random.uniform(-10, 10)
        if now < self.timers['fire']: spawn_particles(self.rect.centerx, self.rect.centery, RED, 2, 2, p_type="FIRE")
        if now < self.timers['ink']: spawn_particles(self.rect.centerx, self.rect.centery, BLACK, 1, 2, p_type="INK")
        if now < self.timers['poison']: spawn_particles(self.rect.centerx, self.rect.centery, GREEN, 1, 2, p_type="POISON")
        if now < self.timers['sticky'] and self.sticky_target:
            if self.sticky_target not in paddles: self.sticky_target = None; return False
            paddle = self.sticky_target
            if paddle.rect.centerx < SCREEN_WIDTH // 2: self.rect.left = paddle.rect.right
            else: self.rect.right = paddle.rect.left
            self.rect.centery = paddle.rect.centery; return True
        return False

    def move(self):
        if self.update_effects(): return
        if self.portal_cooldown > 0: self.portal_cooldown -= 1
        self.rect.x += int(self.speed_x)
        self.speed_y += self.gravity_scale
        self.rect.y += int(self.speed_y + self.extra_vel_y)
        if random.random() < 0.4:
            pt = "SOLID_TRAIL" if self.timers['flash'] > 0 else "TRAIL"
            spawn_particles(self.rect.centerx, self.rect.centery, self.color, count=1, size=4, p_type=pt)
        if self.wrap_around:
            if self.rect.bottom < 0: self.rect.top = SCREEN_HEIGHT
            elif self.rect.top > SCREEN_HEIGHT: self.rect.bottom = 0
        if not self.is_ghost and self.timers['flash'] < pygame.time.get_ticks():
            for obs in obstacles:
                if self.rect.colliderect(obs.rect):
                    if obs.o_type == "BLIND": continue
                    if obs.team == self.last_hit_team and obs.o_type in ["THORN", "WALL", "ICE", "MINE"]: continue
                    if self.is_fake: return "REMOVE"
                    if obs.o_type == "THORN":
                        spawn_particles(self.rect.centerx, self.rect.centery, GREEN, 20, p_type="SHARD")
                        if abs(self.speed_x) > 5: self.speed_x *= 0.1; self.speed_y = random.choice([-2, 2])
                        return
                    elif obs.o_type == "PORTAL":
                        if self.portal_cooldown == 0:
                            spawn_particles(self.rect.centerx, self.rect.centery, PURPLE, 20, p_type="IMPLODE")
                            other_portals = [o for o in obstacles if o.o_type == "PORTAL" and o != obs]
                            if other_portals:
                                target = random.choice(other_portals); self.rect.center = target.rect.center
                                self.portal_cooldown = 60
                            else: self.rect.center = (SCREEN_WIDTH//2, random.randint(100, SCREEN_HEIGHT-100))
                            self.speed_x *= -1
                        return
                    elif obs.o_type == "ICE":
                        spawn_particles(self.rect.centerx, self.rect.centery, CYAN, 10, p_type="SHARD")
                        obstacles.remove(obs); self.speed_x *= -1; return
                    elif obs.o_type == "MIRROR":
                        spawn_particles(self.rect.centerx, self.rect.centery, SILVER, 10, p_type="STAR")
                        self.speed_x *= -1; return
                    elif obs.o_type == "BUMPER":
                        spawn_particles(self.rect.centerx, self.rect.centery, GOLD, 10, p_type="BOLT")
                        self.speed_x *= 1.5; self.speed_y *= 1.5; self.speed_x *= -1; return
                    elif obs.o_type == "MINE":
                        spawn_center_effect("BOOM!", DARK_GRAY)
                        spawn_particles(self.rect.centerx, self.rect.centery, ORANGE, 30, p_type="EXPLODE")
                        obstacles.remove(obs); self.speed_x *= 2.0; self.speed_y = random.choice([-15, 15]); return
                    else:
                        if abs(self.rect.centerx - obs.rect.centerx) > abs(self.rect.centery - obs.rect.centery): self.speed_x *= -1
                        else: self.speed_y *= -1
                        spawn_particles(self.rect.centerx, self.rect.centery, BROWN, 5, symbol="■", p_type="SHOCKWAVE")
        if not self.wrap_around:
            if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.speed_y *= -1
                if self.gravity_scale > 0: self.speed_y *= 0.8
                # 리코셰: 벽 반사마다 가속
                self.bounce_count += 1
                spawn_particles(self.rect.centerx, self.rect.y, self.color, count=5)

    def draw(self, surface):
        if self.visible:
            if self.is_fake:
                s = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (*self.color, 150), (0,0,20,20)); surface.blit(s, self.rect)
            else:
                pygame.draw.ellipse(surface, self.color, self.rect)
                if abs(self.speed_x) > 15:
                    pygame.draw.ellipse(surface, (*self.color, 100), (self.rect.x - self.speed_x, self.rect.y - self.speed_y, 20, 20))

# --- 5. 전역 변수 ---
game_mode = "AI"
paddles = []
score_team1 = 0
score_team2 = 0
ball = Ball()

# =====================================================================
# --- 6. 스킬 시스템 (컨셉 완전 재구현) ---
# =====================================================================

def use_ability(user, type, ball_ref):
    if user.ability_id not in ABILITIES: return False
    opponents = [p for p in paddles if p.team != user.team]
    allies = [p for p in paddles if p.team == user.team]
    cost = COST_BASIC if type == "BASIC" else COST_SKILL if type == "SKILL" else COST_ULT
    if user.stamina < cost:
        spawn_text(user.rect.centerx, user.rect.top - 20, "기력 부족!", GRAY); return False
    if type == "BASIC":
        user.stamina -= cost
        ball_ref.speed_x *= 1.2; ball_ref.color = user.color
        spawn_text(user.rect.centerx, user.rect.top - 30, "강타!", user.color)
        beam_spd = 12 if user.team == TEAM_1 else -12
        spawn_particles(user.rect.centerx, user.rect.centery, user.color, count=5, speed=beam_spd, size=4, p_type="BEAM")
        return True

    user.stamina -= cost
    # 쿨다운 기록
    now = pygame.time.get_ticks()
    if type == "SKILL": user.last_skill_used = now
    elif type == "ULT": user.last_ult_used = now

    aid = user.ability_id
    txt_x, txt_y = user.rect.centerx, user.rect.top - 30

    if aid == 19:  # 복사술사
        aid = random.randint(0, 209)
        spawn_text(txt_x, txt_y - 40, f"Copy: {ABILITIES.get(aid, ABILITIES[0]).name}", WHITE)

    ability_data = ABILITIES.get(aid, ABILITIES[0])
    skill_name_text = ability_data.q_name if type == "SKILL" else ability_data.sp_name
    spawn_text(txt_x, txt_y, skill_name_text, user.color)

    # 파티클 타입 결정
    ptype = "EXPLODE"
    if aid in [0, 39, 109, 159, 177, 186]: ptype = "FIRE"
    elif aid in [1, 114, 27, 160]: ptype = "SHARD"
    elif aid in [28, 15, 101]: ptype = "HEART"
    elif aid in [35, 100, 67, 12]: ptype = "BOLT"
    elif aid in [50, 87, 113, 22, 172]: ptype = "BUBBLE"
    elif aid in [10, 146, 72, 128, 67, 165]: ptype = "GLITCH"
    elif aid in [53, 140, 124, 121]: ptype = "NOTE"
    elif aid in [111, 134, 168]: ptype = "STAR"
    elif aid in [18, 164, 187]: ptype = "POISON"
    elif aid in [151, 171, 181]: ptype = "INK"
    elif aid in [166]: ptype = "RAINBOW"

    # ---------------------------------------------------------------
    # 능력별 개별 기믹 로직
    # ---------------------------------------------------------------

    # === 그룹 A: 불/화염 계열 ===
    if aid in [0, 20, 39, 41, 109, 159, 177, 186]:
        spd_mult = 2.5 if type == "ULT" else 1.6
        ball_ref.speed_x *= spd_mult
        ball_ref.apply_effect('fire', 3000)
        if aid == 109:  # 태양: 상대 기력도 감소
            for op in opponents: op.stamina = max(0, op.stamina - 30)
            spawn_center_effect("SOLAR FLARE", ORANGE)
        if aid == 159: spawn_center_effect("FLOOR IS LAVA", RED)
        if aid == 177:
            for _ in range(3):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 50, 50, 4000, "WALL", color=DARK_GRAY, team=user.team))
        if aid == 186: spawn_center_effect("FIREWORKS!", RED); ball_ref.speed_x *= 1.5

    # === 그룹 B: 시야 방해 ===
    elif aid in [28, 46, 48, 83, 97, 112, 134, 151, 73, 171, 176, 180, 181, 182, 183, 187, 188, 189]:
        full_cover = (type == "ULT") or (aid in [180, 181, 183, 189])
        count = 20 if type == "ULT" else 10
        color_map = {28:PINK, 48:(101,67,33), 112:WHITE, 83:WHITE, 176:DARK_GRAY, 180:BLACK, 181:BLACK, 182:(237,201,175), 183:(0,0,50), 187:(100,100,100), 189:BLACK}
        color = color_map.get(aid, user.color)
        for op in opponents: spawn_blind_obstacles(op, color, count, full_cover=full_cover)
        if aid == 182:
            for op in opponents: op.apply_effect('stunned', 2000)

    # === 그룹 C: 빙결 / 시간 정지 / 벽 ===
    elif aid in [1, 4, 23, 71, 114, 135, 160, 161, 173, 184, 203, 206, 209]:
        duration = 3000 if type == "ULT" else 1500
        if aid == 209:
            for i in range(3):
                obstacles.append(Obstacle(SCREEN_WIDTH//2, 100+i*150, 30, 100, 6000, "WALL", color=BROWN, team=user.team))
        elif aid == 206:
            ball_ref.apply_effect('wrap', 5000); spawn_center_effect("WRAP AROUND", YELLOW)
        elif aid == 203:
            for op in opponents: op.apply_effect('stunned', 2000)
            ball_ref.apply_effect('stop', 2000); spawn_center_effect("THE WORLD", GOLD)
        elif aid == 160:
            for i in range(3):
                obstacles.append(Obstacle(SCREEN_WIDTH//2 + random.randint(-50,50), 100+i*150, 40, 140, 5000, "ICE", team=user.team))
        elif aid == 173:
            for _ in range(5):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 30, 30, 5000, "WALL", color=ORANGE, team=user.team))
        elif aid == 161:
            ball_ref.speed_x *= 2.0; spawn_center_effect("TIME ACCEL", GOLD)
        elif aid == 4:
            ball_ref.apply_effect('stop', 1000); ball_ref.speed_x *= 3.0
        elif aid == 135:
            ball_ref.reset(1 if ball_ref.speed_x > 0 else -1); spawn_center_effect("REWIND", SILVER)
        elif aid == 184:
            for op in opponents: op.apply_effect('frozen', 3000)
            obstacles.append(Obstacle(SCREEN_WIDTH//2, 0, 100, SCREEN_HEIGHT, 3000, "WALL", color=GRAY, team=user.team))
        else:
            for op in opponents: op.apply_effect('frozen', duration)

    # === 그룹 D: 해킹 / 조작 교란 ===
    elif aid in [10, 67, 102, 125, 149, 165, 200, 204, 207]:
        if aid == 207:  # 뱀파이어 로드: 상대 크기 훔치기
            user.apply_effect('giant', 5000)
            for op in opponents: op.apply_effect('shrunk', 5000)
        elif aid == 204:  # 슈링커
            for op in opponents:
                op.apply_effect('shrunk', 5000)
                spawn_particles(op.rect.centerx, op.rect.centery, TEAL, 10, p_type="SHOCKWAVE")
        elif aid == 200:  # 체인저: 위치 스왑
            if opponents:
                target = opponents[0]; user.rect.y, target.rect.y = target.rect.y, user.rect.y
                spawn_center_effect("SWITCH!", MAGENTA)
        elif aid == 165:  # 글리치: 공 순간이동 + 렉
            ball_ref.rect.center = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100))
            ball_ref.apply_effect('lag', 3000)
        elif aid == 67:  # 크래커: 렉 + 글리치 파티클
            ball_ref.apply_effect('lag', 3000)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, LIME, 20, p_type="GLITCH")
        elif aid == 10:  # 해커: 조작키 반전
            for op in opponents: op.apply_effect('reversed', 4000)
        elif aid == 102:  # 최면술사: 혼란
            for op in opponents: op.apply_effect('confused', 4000)
        elif aid == 125:  # 편의점 알바: 공 정지 (바코드 찍기)
            ball_ref.apply_effect('stop', 1500)
            spawn_text(ball_ref.rect.centerx, ball_ref.rect.centery - 30, "BEEP!", ORANGE)
        elif aid == 149:  # 갓파더: 상대를 공포로 얼게 함 (frozen이 맞음)
            for op in opponents: op.apply_effect('frozen', 2500)
            spawn_center_effect("AN OFFER...", BLACK)

    # === 그룹 E: 저격 / 직선 고속 ===
    elif aid in [8, 37, 88, 143, 21, 153, 56, 147, 208]:
        spd = 30 if type == "ULT" else 20
        ball_ref.speed_x = spd if user.team == TEAM_1 else -spd
        ball_ref.speed_y = 0
        if aid == 208:  # 리코셰: 꺾이는 각도로 발사
            ball_ref.speed_y = random.choice([-12, 12])
            ball_ref.bounce_count = 0
        if aid in [56, 147, 21]:  # 궤적 미리보기
            ball_ref.apply_effect('guide', 4000)
        if aid == 21:  # 사이보그: 궤적 분석 후 정밀 발사
            spawn_center_effect("TARGET LOCKED", TEAL)
        if aid == 153:
            spawn_center_effect("UNSTOPPABLE", SILVER)
        ball_ref.apply_effect('flash', 1500)

    # === 그룹 F: 도박 / 랜덤 ===
    elif aid in [5, 63, 92, 166, 167]:
        dice = random.random()
        if aid == 166:
            user.stamina = 100; user.rect.height = user.original_height * 2
            spawn_center_effect("LUCKY!", YELLOW)
        elif aid == 167:
            for op in opponents: op.stamina = 0; op.apply_effect('shrunk', 3000)
            spawn_center_effect("BAD LUCK...", GRAY)
        elif aid == 63:  # 광인: 공이 완전 랜덤 방향
            ball_ref.speed_x = random.choice([-18, -15, 15, 18])
            ball_ref.speed_y = random.choice([-15, -10, 10, 15])
            spawn_center_effect("CHAOS!", PINK)
        elif aid == 92:  # 타짜: 공 위치 바꿔치기
            ball_ref.rect.centery = random.randint(50, SCREEN_HEIGHT-50)
            ball_ref.speed_x *= 1.5
        else:  # 도박사
            if dice < 0.4: ball_ref.speed_x *= 3.5; spawn_center_effect("JACKPOT!!", GOLD)
            elif dice < 0.5: user.stamina = 0; spawn_text(user.rect.centerx, user.rect.y, "BANKRUPT", GRAY)
            else:
                for op in opponents: op.apply_effect('stunned', 2000)

    # === 그룹 G: 소환 / 건설 / 구조물 ===
    elif aid in [13, 15, 49, 74, 104, 131, 77, 25, 150, 157, 162, 169, 170, 172, 174, 175, 178, 179, 185, 201, 202]:
        if aid == 202:  # 도플갱어
            helper = Paddle(user.rect.x + (50 if user.team==TEAM_1 else -50), user.rect.y, is_ai=True, team=user.team, duration=8000)
            helper.color = user.color; helper.stamina = 0; helper.stamina_regen = 0; helper.ability_id = -1
            paddles.append(helper)
        elif aid == 201:  # 마인 레이어
            for _ in range(3 if type=="SKILL" else 6):
                obstacles.append(Obstacle(random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100), 30, 30, 9999, "MINE", team=user.team))
        elif aid == 172:  # 양봉업자
            obstacles.append(Obstacle(SCREEN_WIDTH//2, 0, 40, SCREEN_HEIGHT, 6000, "THORN", color=(255, 200, 0), team=user.team))
        elif aid == 174:  # 도서관 사서: 책장 벽
            obstacles.append(Obstacle(SCREEN_WIDTH//2 - 20, 100, 40, 400, 6000, "WALL", color=(139, 69, 19), team=user.team))
        elif aid == 175:  # 라면 요리사: 꼬불꼬불 장애물
            for _ in range(10):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 60, 10, 4000, "WALL", color=(255, 255, 150), team=user.team))
        elif aid == 178:  # 뱀파이어 헌터: 십자가
            obstacles.append(Obstacle(SCREEN_WIDTH//2 - 10, 100, 20, 300, 5000, "WALL", color=SILVER, team=user.team))
            obstacles.append(Obstacle(SCREEN_WIDTH//2 - 100, 150, 200, 20, 5000, "WALL", color=SILVER, team=user.team))
        elif aid == 179:  # 국왕: 성벽
            obstacles.append(Obstacle(SCREEN_WIDTH//2, 0, 50, SCREEN_HEIGHT, 8000, "WALL", color=GOLD, team=user.team))
        elif aid == 170:  # 테트리스
            for _ in range(5):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(0, 200), 40, 40, 5000, "WALL", color=random.choice([CYAN, YELLOW, PURPLE, RED, GREEN]), team=user.team))
        elif aid == 169:  # 창조주
            for _ in range(5):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 50, 50, 5000, "WALL", team=user.team))
        elif aid == 162:  # 거울 벽
            obstacles.append(Obstacle(SCREEN_WIDTH//2, 0, 20, SCREEN_HEIGHT, 5000, "MIRROR", team=user.team))
        elif aid == 157:  # 대장군: 화살비
            spawn_center_effect("ARROW RAIN", BROWN)
            for _ in range(10):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(0, SCREEN_HEIGHT), 10, 50, 2000, "THORN", team=user.team))
        elif aid == 150:  # 도자기: 얼음 장애물
            obstacles.append(Obstacle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100, 40, 200, 4000, "ICE", team=user.team))
        elif aid in [13, 74]:  # 건축가, 건물주
            obs_x = SCREEN_WIDTH//2 + random.randint(-50, 50)
            for i in range(3):
                obstacles.append(Obstacle(obs_x, 100+i*150, 40, 140, 6000, "WALL", team=user.team))
        elif aid == 77:  # 정원사: 가시
            for _ in range(3):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 50, 50, 8000, "THORN", team=user.team))
        elif aid == 25:  # 외계인: 포털
            obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 60, 60, 5000, "PORTAL", team=user.team))
        elif aid == 185:  # 좀비 군단장: 가짜 공 무리
            for _ in range(8):
                fake = Ball(is_fake=True)
                fake.rect.center = ball_ref.rect.center
                fake.speed_x = ball_ref.speed_x * random.uniform(0.8, 1.2)
                fake.speed_y = random.uniform(-15, 15); fake.color = GREEN
                fake_balls.append(fake)
        else:  # 환술사, 광대, 서커스 단장 등 가짜공
            cnt = 5 if type == "ULT" else 2
            for _ in range(cnt):
                fake = Ball(is_fake=True)
                fake.rect.center = ball_ref.rect.center
                fake.speed_x = ball_ref.speed_x * random.uniform(0.9, 1.1)
                fake.speed_y = random.uniform(-10, 10); fake.color = user.color
                fake_balls.append(fake)

    # === 그룹 H: 은신 ===
    elif aid in [7, 54, 98, 115, 133, 163]:
        duration = 2500
        if aid == 7:  # 닌자: 공만 사라짐 + 순간이동
            ball_ref.apply_effect('invisible', duration)
            ball_ref.rect.centerx = SCREEN_WIDTH // 2
        elif aid == 163:  # 그림자: 잔상 파티클
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, BLACK, 20, p_type="IMPLODE")
            ball_ref.apply_effect('invisible', duration)
        else:
            ball_ref.apply_effect('invisible', duration)
            for ally in allies: ally.apply_effect('invisible', duration)

    # === 그룹 I: 흡수 / 독 / 전염 ===
    elif aid in [6, 11, 61, 138, 144, 9, 18, 155, 164]:
        if aid == 164:  # 역병의사: 감염
            for op in opponents: op.apply_effect('infected', 5000)
            spawn_center_effect("PLAGUE", PURPLE)
        elif aid == 155:  # 드라큘라: 기력 대량 흡혈
            for op in opponents: op.stamina = max(0, op.stamina - 50)
            user.stamina = min(100, user.stamina + 50)
            spawn_center_effect("BLOOD SUCK", CRIMSON)
        elif aid in [9, 96]:  # 치유사, 천사
            for ally in allies:
                ally.stamina = min(100, ally.stamina + 50)
                ally.apply_effect('speed_boost', 3000)
                spawn_particles(ally.rect.centerx, ally.rect.centery, GREEN, 15, symbol="HEAL", p_type="RISE")
        elif aid == 18:  # 독술사
            ball_ref.apply_effect('poison', 5000)
        elif aid == 61:  # 저승사자: 기력을 0으로
            for op in opponents: op.stamina = 0
            spawn_center_effect("SOUL REAP", (20, 20, 80))
        elif aid == 66:  # CEO: 기력 빼앗기 (뇌물)
            drain = 50
            for op in opponents: op.stamina = max(0, op.stamina - drain)
            user.stamina = min(100, user.stamina + drain)
            spawn_center_effect("DEAL!", GOLD)
        elif aid == 138:  # 리치: 흡혈 + 부활
            for op in opponents: op.stamina = max(0, op.stamina - 30)
            user.stamina = min(100, user.stamina + 30)
            user.timers['revive'] = pygame.time.get_ticks() + 10000
            spawn_center_effect("LICH PACT", PURPLE)
        else:  # 일반 흡수 (뱀파이어, 네크로맨서 등)
            drain = 40
            for op in opponents: op.stamina = max(0, op.stamina - drain); spawn_particles(op.rect.centerx, op.rect.centery, RED, 15, symbol="-HP", p_type="RISE")
            for ally in allies: ally.stamina = min(100, ally.stamina + drain); spawn_particles(ally.rect.centerx, ally.rect.centery, GREEN, 15, symbol="+HP", p_type="RISE")

    # === 그룹 J: 물리 변조 (파동/중력/염동력) ===
    elif aid in [16, 50, 52, 70, 89, 136, 22, 35, 152, 158, 154, 205, 3, 2, 26, 42, 62, 79, 108, 110]:
        if aid == 3:  # 거인
            user.apply_effect('giant', 5000)
        elif aid == 152:  # 고무인간
            user.apply_effect('giant', 5000)
        elif aid == 205:  # 그라비티 웰: 중력 당김
            ball_ref.apply_effect('gravity', 4000)
            spawn_center_effect("BLACK HOLE", PURPLE)
        elif aid == 158:  # 폭풍의 눈: 중앙으로 당김
            ball_ref.apply_effect('magnet', 3000)
            dummy = Paddle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            ball_ref.magnet_target = dummy
        elif aid == 22:  # 슬라임: 끈적이게
            ball_ref.apply_effect('sticky', 1000); ball_ref.sticky_target = user
        elif aid == 35:  # 전기 기술자: 감전
            ball_ref.apply_effect('shock', 3000)
            for op in opponents: op.apply_effect('stunned', 1500)
            spawn_center_effect("SHOCK!", YELLOW)
        elif aid == 136:  # 공간 절단자: 공 순간이동
            ball_ref.rect.center = (SCREEN_WIDTH//2, random.randint(100, SCREEN_HEIGHT-100))
            ball_ref.speed_x *= -1
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, user.color, 20, p_type="IMPLODE")
        elif aid == 154:  # 양자: 가짜 공 하나 소환 (중첩)
            fake = Ball(is_fake=True)
            fake.rect.center = ball_ref.rect.center
            fake.speed_x = ball_ref.speed_x * -1
            fake.speed_y = ball_ref.speed_y * random.uniform(0.8, 1.2)
            fake.color = TEAL; fake_balls.append(fake)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, TEAL, 20, p_type="SPIRAL")
        elif aid == 108:  # 포병: 중력 강화 + 하향 곡선
            ball_ref.gravity_scale = 0.5
            ball_ref.speed_x = (18 if user.team == TEAM_1 else -18)
            spawn_center_effect("FIRE!", GREEN)
        elif aid == 110:  # 달: 중력 감소 (반중력)
            ball_ref.apply_effect('gravity_flip', 3000)
            spawn_center_effect("LOW GRAVITY", YELLOW)
        elif aid == 79:  # 파일럿: 상승 곡선
            ball_ref.speed_y = -15; ball_ref.speed_x *= 1.5
            spawn_center_effect("TAKEOFF!", SILVER)
        elif aid == 2:  # 바람의 신: 파동
            ball_ref.apply_effect('wave', 4000)
        elif aid == 26:  # 테니스: 파동 + 가속
            ball_ref.apply_effect('wave', 3000); ball_ref.speed_x *= 1.4
        elif aid == 62:  # 투우사: 파동 + 빠름
            ball_ref.apply_effect('wave', 3000); ball_ref.speed_x *= 1.5
        elif aid in [42, 89]:  # 기상캐스터, 축구선수
            ball_ref.apply_effect('wave', 3000)
        elif aid in [16, 52]:  # 중력술사, 우주인
            ball_ref.apply_effect('gravity', 3000)
        elif aid == 70:  # 수학쌤: 사인파
            ball_ref.apply_effect('wave', 4000)
        elif aid == 50:  # 서퍼: 물결
            ball_ref.apply_effect('wave', 4000)
        else:
            ball_ref.speed_x *= 1.3

    # === 그룹 K: 속도 조작 ===
    elif aid in [55, 59, 99, 14, 30, 38, 45, 53, 58, 76, 78, 86, 93, 121, 123, 126, 65, 94, 47, 71, 107]:
        if aid == 55:  # 바이킹: 자신 속도 대폭 상승
            user.apply_effect('speed_boost', 5000)
            user.current_speed = user.base_speed * 2.5
            spawn_center_effect("BERSERK!", BROWN)
        elif aid == 59:  # 늑대인간: 속도+공 파워
            user.apply_effect('speed_boost', 5000)
            ball_ref.speed_x *= 1.8; spawn_center_effect("BLOODLUST!", DARK_GRAY)
        elif aid == 99:  # 더 히어로: 전체 버프
            user.apply_effect('speed_boost', 4000); user.apply_effect('giant', 4000)
            user.stamina = min(100, user.stamina + 30); spawn_center_effect("HERO TIME!", BLUE)
        elif aid == 14:  # 광전사: 체력 낮을수록 가속
            rage_mult = 1.0 + (1.0 - user.stamina / 100) * 2.5
            ball_ref.speed_x *= rage_mult; spawn_center_effect(f"RAGE x{rage_mult:.1f}!", RED)
        elif aid == 30:  # 무도가: 장풍 (공 가속)
            push = 1 if user.team == TEAM_1 else -1
            ball_ref.speed_x = push * 22; ball_ref.speed_y = 0
            spawn_center_effect("HADOUKEN!", YELLOW)
        elif aid == 38:  # 사무라이: 순간 가속 + 직선
            ball_ref.speed_x *= 2.2; ball_ref.speed_y = 0
            spawn_center_effect("IAIDO!", CRIMSON)
        elif aid == 45:  # 미식축구: 공 강타
            ball_ref.speed_x *= 2.0; ball_ref.speed_y = random.choice([-5, 5])
            spawn_center_effect("TOUCHDOWN!", (165,42,42))
        elif aid == 53:  # 락스타: 공 흔들기 (wobble)
            ball_ref.apply_effect('wobble', 3000)
            spawn_center_effect("DEATH METAL!", PURPLE)
        elif aid == 58:  # 연금술사: 공을 무겁게 (중력 증가 + 느려짐)
            ball_ref.gravity_scale = 0.7; ball_ref.speed_x *= 0.7
            spawn_center_effect("GOLD BALL", GOLD)
        elif aid == 76:  # 배달원: 가속 후 감속 (wave)
            ball_ref.speed_x *= 2.5
            spawn_center_effect("TURBO!", MINT)
        elif aid == 78:  # 소방관: 공을 강하게 밀어냄
            push = 1 if user.team == TEAM_1 else -1
            ball_ref.speed_x = push * 20; ball_ref.speed_y = random.choice([-8, 8])
            spawn_center_effect("WATER CANNON!", RED)
        elif aid == 86:  # 외교관: 공 속도 반으로
            ball_ref.speed_x *= 0.4; ball_ref.speed_y *= 0.4
            spawn_center_effect("PEACE...", BLUE)
        elif aid == 93:  # 래퍼: 리듬에 맞춰 wobble
            ball_ref.apply_effect('wobble', 3000)
            spawn_center_effect("DROP THE BEAT!", BLACK)
        elif aid == 121:  # ASMR: 극도로 느리게
            ball_ref.speed_x *= 0.2; ball_ref.speed_y *= 0.2
            spawn_center_effect("shhh...", PINK)
        elif aid == 123:  # 헬창: 무겁고 빠름
            ball_ref.speed_x *= 1.8; ball_ref.gravity_scale = 0.3
            spawn_center_effect("3대 500!", BROWN)
        elif aid == 126:  # 주식 트레이더: 랜덤 가속/감속
            dice = random.random()
            if dice < 0.5: ball_ref.speed_x *= 3.0; spawn_center_effect("떡상!", RED)
            else: ball_ref.speed_x *= 0.3; spawn_center_effect("떡락...", GRAY)
        elif aid == 65:  # 스님: 속도 초기화
            ball_ref.speed_x = (9 if ball_ref.speed_x > 0 else -9); ball_ref.speed_y = random.choice([-7, 7])
            spawn_center_effect("정적...", ORANGE)
        elif aid == 94:  # 감독: 공 멈춤 (컷!)
            ball_ref.apply_effect('stop', 2000); spawn_center_effect("CUT!", WHITE)
        elif aid == 47:  # 조련사: 공 멈춤 (기다려)
            ball_ref.apply_effect('stop', 1500); spawn_center_effect("기다려!", (205,133,63))
        elif aid == 71:  # 교통경찰: 공 정지
            ball_ref.apply_effect('stop', 2000); spawn_center_effect("STOP!", BLUE)
        elif aid == 107:  # 청소기: 공 흡입 후 정지
            ball_ref.apply_effect('stop', 1000)
            # 내 쪽으로 당기기
            ball_ref.magnet_target = user; ball_ref.apply_effect('magnet', 800)
            spawn_center_effect("SUCTION!", SILVER)
        else:
            ball_ref.speed_x *= 1.5

    # === 그룹 L: 패들 크기 조작 ===
    elif aid in [43, 43, 96, 3]:
        if aid == 43:  # 판사: 상대 패들 축소
            for op in opponents: op.apply_effect('shrunk', 4000)
            spawn_center_effect("GUILTY!", WHITE)
        elif aid == 96:  # 천사: 자신 패들 확대 + 기력회복
            user.apply_effect('giant', 4000)
            user.stamina = min(100, user.stamina + 40)
            spawn_center_effect("DIVINE!", GOLD)

    # === 그룹 M: 자기력 / 당기기 / 밀기 ===
    elif aid in [12, 44, 120, 127, 106, 122]:
        if aid == 12:  # 자석 인간: 공을 내 쪽으로
            ball_ref.apply_effect('magnet', 3000); ball_ref.magnet_target = user
            spawn_center_effect("ATTRACT!", MAGENTA)
        elif aid == 44:  # 낚시꾼: 공을 강제로 내 쪽으로 당김
            # 공을 순간적으로 내 방향으로 튕김
            pull = 1 if user.team == TEAM_1 else -1
            ball_ref.speed_x = pull * abs(ball_ref.speed_x) * 1.5
            spawn_center_effect("CATCH!", (0, 191, 255))
            spawn_particles(user.rect.centerx, user.rect.centery, (0, 191, 255), 20, p_type="IMPLODE")
        elif aid == 127:  # 렉카: 공을 강제로 끌어당김
            pull = 1 if user.team == TEAM_1 else -1
            ball_ref.speed_x = pull * 20
            spawn_center_effect("TOWING!", YELLOW)
        elif aid == 120:  # 드론: 공 유도 (magnet)
            ball_ref.apply_effect('magnet', 4000); ball_ref.magnet_target = user
            spawn_center_effect("LOCKED ON", TEAL)
        elif aid == 106:  # 강아지: 공을 쫓아다님 (magnet)
            ball_ref.apply_effect('magnet', 3000); ball_ref.magnet_target = user
            spawn_particles(user.rect.centerx, user.rect.centery, BROWN, 10, symbol="🐕", p_type="RISE")
        elif aid == 122:  # 민트초코: 랜덤 밀거나 당김
            if random.random() < 0.5:
                ball_ref.apply_effect('magnet', 2000); ball_ref.magnet_target = user
                spawn_center_effect("좋아!", MINT)
            else:
                push = -1 if user.team == TEAM_1 else 1
                ball_ref.speed_x = push * 20
                spawn_center_effect("싫어!", (200, 50, 50))

    # === 그룹 N: 특수 패들 효과 ===
    elif aid in [11, 17, 85, 95, 139, 129]:
        if aid == 11:  # 네크로맨서: 부활 예약
            user.timers['revive'] = pygame.time.get_ticks() + 15000
            spawn_center_effect("UNDYING!", (50, 0, 50))
        elif aid == 17:  # 반사 전문가: 오토 가드
            user.apply_effect('auto_defend', 3000)
            spawn_center_effect("AUTO GUARD!", WHITE)
        elif aid == 85:  # 보디가드: 방패 (mirror 장애물을 내 앞에)
            shield_x = user.rect.right + 5 if user.team == TEAM_1 else user.rect.left - 25
            obstacles.append(Obstacle(shield_x, user.rect.centery - 60, 20, 120, 4000, "MIRROR", team=user.team))
            spawn_center_effect("SHIELD!", BLACK)
        elif aid == 95:  # 좀비: 부활 + 느려짐
            user.timers['revive'] = pygame.time.get_ticks() + 10000
            user.apply_effect('infected', 3000)  # 느려짐 표현
            spawn_center_effect("ZOMBIE!", GREEN)
        elif aid == 139:  # 성기사: 오토 가드 + 강화
            user.apply_effect('auto_defend', 4000)
            user.apply_effect('speed_boost', 4000)
            spawn_center_effect("DIVINE SHIELD!", GOLD)
        elif aid == 129:  # 고인물: 자신 오토 방어 + 상대 혼란
            user.apply_effect('auto_defend', 3000)
            for op in opponents: op.apply_effect('confused', 2000)
            spawn_center_effect("고인물...", DARK_GRAY)

    # === 그룹 O: 렉 / 버그 / 특이한 공 움직임 ===
    elif aid in [40, 64, 68, 69, 72, 80, 81, 82, 84, 87, 90, 91, 100, 103, 111, 105, 116, 117, 119, 130, 132, 140, 145, 146]:
        if aid == 40:  # 유령: 공 고스트 모드
            ball_ref.is_ghost = True; ball_ref.apply_effect('invisible', 2000)
            spawn_center_effect("GHOST BALL!", (200,200,255))
        elif aid == 64:  # 발레리나: 우아한 wave
            ball_ref.apply_effect('wave', 4000)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, WHITE, 20, p_type="STAR")
        elif aid == 68:  # 시간여행자: 공 초기화 (리셋)
            ball_ref.reset(1 if ball_ref.speed_x > 0 else -1)
            spawn_center_effect("REWIND!", CYAN)
        elif aid == 69:  # 개발자: 렉 + 랜덤 텔레포트
            ball_ref.apply_effect('lag', 3000)
            ball_ref.rect.center = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100))
            spawn_center_effect("UNDEFINED", BLUE)
        elif aid == 72:  # 게이머: 렉
            ball_ref.apply_effect('lag', 3000); spawn_center_effect("LAG!", LIME)
        elif aid == 80:  # 광부: 돌덩이 장애물 3개
            for _ in range(3):
                obstacles.append(Obstacle(random.randint(150, SCREEN_WIDTH-150), random.randint(100, SCREEN_HEIGHT-100), 40, 40, 5000, "WALL", color=GRAY, team=user.team))
            spawn_center_effect("ROCKS!", GOLD)
        elif aid == 81:  # 사육사: 완전 랜덤 wobble
            ball_ref.apply_effect('wobble', 4000); spawn_center_effect("WILD!", ORANGE)
        elif aid == 82:  # 점술가: 궤적 미리보기
            ball_ref.apply_effect('guide', 5000); spawn_center_effect("FORESEEN...", PURPLE)
        elif aid == 84:  # 탐정: 가짜 공 소환 (진짜 찾아라)
            for _ in range(4):
                fake = Ball(is_fake=True)
                fake.rect.center = ball_ref.rect.center
                fake.speed_x = ball_ref.speed_x * random.uniform(0.9, 1.1)
                fake.speed_y = random.uniform(-12, 12); fake.color = WHITE
                fake_balls.append(fake)
        elif aid == 87:  # 해녀: 물방울 장애물
            for _ in range(5):
                obstacles.append(Obstacle(random.randint(150, SCREEN_WIDTH-150), random.randint(100, SCREEN_HEIGHT-100), 30, 30, 4000, "BUMPER", team=user.team))
        elif aid == 90:  # 농부: 공 분열 → 가짜 공 소환
            for _ in range(4):
                fake = Ball(is_fake=True)
                fake.rect.center = ball_ref.rect.center
                fake.speed_x = ball_ref.speed_x * random.uniform(0.8, 1.2)
                fake.speed_y = random.uniform(-10, 10); fake.color = GREEN
                fake_balls.append(fake)
            spawn_center_effect("HARVEST!", GREEN)
        elif aid == 91:  # 패션모델: wave 이동
            ball_ref.apply_effect('wave', 3000)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, PINK, 15, p_type="STAR")
        elif aid == 100:  # 치과의사: 화면 흔들기 + 공 wobble
            shake_effect.start(30, 15); ball_ref.apply_effect('wobble', 2000)
            spawn_center_effect("DRILL!!", WHITE)
        elif aid == 103:  # 바텐더: 취한 공 (wobble)
            ball_ref.apply_effect('wobble', 4000)
            spawn_center_effect("BOTTOMS UP!", ORANGE)
        elif aid == 111:  # 별: 별똥별 장애물
            for _ in range(6):
                obstacles.append(Obstacle(random.randint(100, SCREEN_WIDTH-100), random.randint(0, SCREEN_HEIGHT), 15, 40, 2500, "THORN", color=CYAN, team=user.team))
            spawn_center_effect("STARFALL!", CYAN)
        elif aid == 105:  # 고양이: 공 궤적 살짝 변경 (wobble 약하게)
            ball_ref.speed_y += random.choice([-6, 6])
            ball_ref.apply_effect('wobble', 1500)
            spawn_center_effect("냥~", YELLOW)
        elif aid == 116:  # 무지개: 공 색깔 랜덤 + wave
            ball_ref.color = random.choice([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE])
            ball_ref.apply_effect('wave', 3000)
        elif aid == 117:  # 오로라: 화려한 궤적 (guide + wave)
            ball_ref.apply_effect('wave', 3000); ball_ref.apply_effect('guide', 3000)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, GREEN, 20, p_type="RAINBOW")
        elif aid == 119:  # 차원 관리자: wrap around (화면 끝 통과)
            ball_ref.apply_effect('wrap', 5000); spawn_center_effect("WRAP!", BLACK)
        elif aid == 130:  # 뉴비: 완전 랜덤 wobble + 방향
            ball_ref.speed_x = random.choice([-12, -10, 10, 12]) * (1 if user.team==TEAM_1 else -1)
            ball_ref.speed_y = random.choice([-10, -8, 8, 10])
            ball_ref.apply_effect('wobble', 3000); spawn_center_effect("??", LIME)
        elif aid == 132:  # 골렘: 큰 바위 장애물
            for _ in range(2):
                obstacles.append(Obstacle(random.randint(150, SCREEN_WIDTH-150), random.randint(100, SCREEN_HEIGHT-100), 80, 80, 6000, "WALL", color=GRAY, team=user.team))
            spawn_center_effect("GOLEM!", GRAY)
        elif aid == 140:  # 바드: 음표 장애물
            for _ in range(6):
                obstacles.append(Obstacle(random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100), 25, 25, 4000, "BUMPER", color=PINK, team=user.team))
            spawn_center_effect("♪♫", PINK)
        elif aid == 145:  # 정령사: 랜덤 원소 효과
            elem = random.randint(0, 3)
            if elem == 0: ball_ref.apply_effect('fire', 3000); spawn_center_effect("FIRE SPIRIT!", RED)
            elif elem == 1: ball_ref.apply_effect('wave', 3000); spawn_center_effect("WIND SPIRIT!", CYAN)
            elif elem == 2: ball_ref.apply_effect('gravity', 3000); spawn_center_effect("EARTH SPIRIT!", BROWN)
            else: ball_ref.apply_effect('lag', 2000); spawn_center_effect("THUNDER SPIRIT!", YELLOW)
        elif aid == 146:  # AI 챗봇: 렉 + 생각 중 텍스트
            ball_ref.apply_effect('lag', 4000)
            spawn_text(ball_ref.rect.centerx, ball_ref.rect.centery - 40, "생각 중...", TEAL)
        else:
            ball_ref.speed_x *= 1.4

    # === 그룹 P: 포털 / 공간이동 ===
    elif aid in [191, 192, 193, 194, 195, 196, 197, 198, 199]:
        if aid == 191:
            obstacles.append(Obstacle(200, random.randint(100, SCREEN_HEIGHT-100), 50, 50, 8000, "PORTAL", team=user.team))
            obstacles.append(Obstacle(SCREEN_WIDTH-200, random.randint(100, SCREEN_HEIGHT-100), 50, 50, 8000, "PORTAL", team=user.team))
        elif aid == 192:
            obstacles.append(Obstacle(SCREEN_WIDTH//2, 100, 20, 500, 5000, "MIRROR", team=user.team))
        elif aid == 193:
            push_dir = 1 if user.team == TEAM_1 else -1
            ball_ref.speed_x = push_dir * 25; spawn_center_effect("FORCE PUSH", MINT)
        elif aid == 194:
            ball_ref.apply_effect('flash', 5000)
        elif aid == 195:
            ball_ref.apply_effect('wobble', 3000)
        elif aid == 196:
            ball_ref.is_ghost = True
        elif aid == 197:
            ball_ref.speed_x *= 0.3; ball_ref.apply_effect('stop', 2000)
            spawn_particles(ball_ref.rect.centerx, ball_ref.rect.centery, BLUE, 20, p_type="SPIRAL")
        elif aid == 198:
            for _ in range(5):
                obstacles.append(Obstacle(random.randint(200, SCREEN_WIDTH-200), random.randint(100, SCREEN_HEIGHT-100), 40, 40, 5000, "BUMPER", team=user.team))
        elif aid == 199:
            ball_ref.speed_x = random.choice([-15, 15])
            ball_ref.speed_y = random.choice([-15, 15])
            ball_ref.gravity_scale = random.choice([-0.5, 0.5, 0])
            spawn_center_effect("CHAOS", BLACK)

    # === 그룹 Q: 나머지 (리코셰 등 특수) ===
    else:
        # 리코셰 208은 그룹 E에서 처리됨
        # 기본 fallback: 그래도 컨셉에 맞는 간단 효과
        ball_ref.speed_x *= 1.5
        spawn_particles(user.rect.centerx, user.rect.centery, user.color, 10, p_type="EXPLODE")

    # 리코셰: 현재 bounce_count에 따라 속도 부스트 적용
    if aid == 208 and ball_ref.bounce_count > 0:
        boost = 1.0 + ball_ref.bounce_count * 0.15
        ball_ref.speed_x *= min(boost, 3.0)

    # 판사 / 천사: 여기서 처리 (그룹 L이 if/elif 체인에 안 들어가는 경우 대비)
    if aid == 43 and type in ["SKILL", "ULT"]:
        for op in opponents: op.apply_effect('shrunk', 4000)
    if aid == 96 and type in ["SKILL", "ULT"]:
        user.apply_effect('giant', 4000); user.stamina = min(100, user.stamina + 40)

    if type == "ULT":
        shake_effect.start(15, 10)
        spawn_particles(user.rect.centerx, user.rect.centery, user.color, 40, size=8, p_type=ptype)
    else:
        spawn_particles(user.rect.centerx, user.rect.centery, user.color, 20, size=5, p_type=ptype)

    return True

def get_skill_duration(aid):
    descs = {
        159:"효과: 화염 (접촉 시 화상)", 0:"효과: 화염 (접촉 시 화상)",
        153:"효과: 절대 관통", 44:"효과: 공 강제 당김",
        55:"효과: 자신 속도 2.5배", 58:"효과: 공 무거워짐(중력)",
        66:"효과: 상대 기력 흡수", 80:"효과: 돌 장애물 생성",
        93:"효과: 공 wobble", 105:"효과: 궤적 변경",
        119:"효과: wrap around(화면 순환)", 129:"효과: 오토 방어 + 적 혼란",
        149:"효과: 상대 공포 마비", 56:"효과: 궤적 미리보기 + 정밀 발사",
        35:"효과: 감전 + 적 마비",
    }
    return descs.get(aid, "효과: 특수 능력 발동")

# --- 7. 장면 관리 ---

def reset_game_state():
    global score_team1, score_team2, field_event, field_event_timer, next_event_time
    score_team1 = 0; score_team2 = 0
    field_event = None; field_event_timer = 0
    next_event_time = pygame.time.get_ticks() + FIELD_EVENT_INTERVAL
    reset_round()

def reset_round():
    if game_mode == "2VS2":
        if len(paddles) == 4:
            paddles[0].rect.centery = SCREEN_HEIGHT // 4
            paddles[1].rect.centery = SCREEN_HEIGHT * 3 // 4
            paddles[2].rect.centery = SCREEN_HEIGHT // 4
            paddles[3].rect.centery = SCREEN_HEIGHT * 3 // 4
    else:
        if len(paddles) == 2:
            paddles[0].rect.centery = SCREEN_HEIGHT // 2
            paddles[1].rect.centery = SCREEN_HEIGHT // 2
    for p in paddles:
        for k in p.timers: p.timers[k] = 0
        p.rect.height = p.original_height
    ball.reset(1 if random.random() > 0.5 else -1)
    particles.clear(); floating_texts.clear(); central_effects.clear(); obstacles.clear(); fake_balls.clear()

def draw_pause_menu(screen, clicked):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(MENU_BG); screen.blit(overlay, (0, 0))
    menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 200, 400, 400)
    pygame.draw.rect(screen, UI_BG, menu_rect, border_radius=20)
    pygame.draw.rect(screen, ACCENT_COLOR, menu_rect, 3, border_radius=20)
    title_surf = FONT_TITLE.render("일시 정지", True, WHITE)
    screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, menu_rect.y + 30))
    mouse_pos = pygame.mouse.get_pos()
    buttons = [("계속 하기", "resume"), ("타이틀로 이동", "restart"), ("게임 종료", "quit")]
    action = None
    for i, (text, cmd) in enumerate(buttons):
        btn_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 120 + i * 80, 300, 60)
        color = ACCENT_COLOR if btn_rect.collidepoint(mouse_pos) else PANEL_BG
        pygame.draw.rect(screen, color, btn_rect, border_radius=10)
        txt_surf = FONT_MAIN.render(text, True, WHITE)
        screen.blit(txt_surf, (btn_rect.centerx - txt_surf.get_width()//2, btn_rect.centery - txt_surf.get_height()//2))
        if btn_rect.collidepoint(mouse_pos) and clicked:
            if SOUND_BUTTON: SOUND_BUTTON.play()
            action = cmd
    return action

# ---------------------------------------------------------------
# HUD 드로잉 (스킬 이름 + 쿨다운 바 표시)
# ---------------------------------------------------------------

def draw_hud(surface, paddle, is_left):
    if paddle.ability_id not in ABILITIES: return
    ab = ABILITIES[paddle.ability_id]
    now = pygame.time.get_ticks()

    hud_x = 10 if is_left else SCREEN_WIDTH - 310
    hud_y = SCREEN_HEIGHT - 130

    # 배경 패널
    panel = pygame.Surface((300, 120), pygame.SRCALPHA)
    panel.fill((15, 18, 35, 200))
    surface.blit(panel, (hud_x, hud_y))

    # 능력 색상 테두리 (기력에 따라 밝기)
    border_alpha = int(180 + (paddle.stamina / 100) * 75)
    pygame.draw.rect(surface, ab.color, (hud_x, hud_y, 300, 120), 2, border_radius=10)

    # 능력 이름 + 플레이버 텍스트
    name_surf = FONT_HUD.render(ab.name, True, ab.color)
    surface.blit(name_surf, (hud_x + 10, hud_y + 7))

    # Q 스킬 행
    q_label = FONT_UI.render(f"[Q] {ab.q_name}", True, YELLOW)
    surface.blit(q_label, (hud_x + 10, hud_y + 32))
    # Q 쿨다운 바
    q_elapsed = now - paddle.last_skill_used
    q_ratio = min(1.0, q_elapsed / max(1, paddle.skill_cooldown_ms))
    bar_w = 150
    pygame.draw.rect(surface, DARK_GRAY, (hud_x + 10, hud_y + 52, bar_w, 8), border_radius=4)
    q_fill_color = YELLOW if q_ratio >= 1.0 else (80, 70, 20)
    pygame.draw.rect(surface, q_fill_color, (hud_x + 10, hud_y + 52, int(bar_w * q_ratio), 8), border_radius=4)
    if q_ratio >= 1.0:
        surface.blit(FONT_UI.render("READY!", True, YELLOW), (hud_x + 164, hud_y + 48))
    else:
        remain_s = max(0, (paddle.skill_cooldown_ms - q_elapsed) / 1000)
        surface.blit(FONT_UI.render(f"{remain_s:.1f}s", True, GRAY), (hud_x + 164, hud_y + 48))

    # SP 궁극기 행
    sp_label = FONT_UI.render(f"[Sp] {ab.sp_name}", True, CYAN)
    surface.blit(sp_label, (hud_x + 10, hud_y + 65))
    # SP = 기력 바
    sp_ratio = paddle.stamina / 100.0
    sp_fill_color = CYAN if sp_ratio >= 1.0 else (20, 80, 100)
    pygame.draw.rect(surface, DARK_GRAY, (hud_x + 10, hud_y + 85, bar_w, 8), border_radius=4)
    pygame.draw.rect(surface, sp_fill_color, (hud_x + 10, hud_y + 85, int(bar_w * sp_ratio), 8), border_radius=4)
    sp_txt = "MAX!" if sp_ratio >= 1.0 else f"SP {int(paddle.stamina)}/100"
    surface.blit(FONT_UI.render(sp_txt, True, CYAN if sp_ratio >= 1.0 else GRAY), (hud_x + 164, hud_y + 81))

    # 기력 만충 시 테두리 펄스 효과
    if paddle.stamina >= 100:
        pulse = int(abs(math.sin(now * 0.005)) * 40)
        glow_col = (min(255, ab.color[0]+pulse), min(255, ab.color[1]+pulse), min(255, ab.color[2]+pulse))
        pygame.draw.rect(surface, glow_col, (hud_x-1, hud_y-1, 302, 122), 3, border_radius=11)

    # 환경 이벤트 상태 표시 (HUD 위)
    if field_event:
        ev_name = next((e[1] for e in FIELD_EVENTS if e[0] == field_event), "")
        ev_color = next((e[2] for e in FIELD_EVENTS if e[0] == field_event), WHITE)
        ev_surf = FONT_UI.render(f"★ {ev_name}", True, ev_color)
        surface.blit(ev_surf, (hud_x, hud_y - 20))

def scene_selection():
    selected_p1 = -1; selected_p2 = -1
    current_page = 0; per_page = 30; step = "MODE"
    global game_mode, paddles
    paused = False; search_text = ""; is_searching = False
    filtered_ids = list(ABILITIES.keys()); temp_p1_ability = 0

    while True:
        clicked = False; screen.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if is_searching:
                    if event.key == pygame.K_BACKSPACE: search_text = search_text[:-1]
                    elif event.key == pygame.K_RETURN: is_searching = False
                    elif event.key == pygame.K_ESCAPE: is_searching = False
                    else: search_text += event.unicode
                    if search_text: filtered_ids = [k for k, v in ABILITIES.items() if search_text in v.name]
                    else: filtered_ids = list(ABILITIES.keys())
                    current_page = 0
                else:
                    if event.key == pygame.K_m: paused = not paused
                    if event.key == pygame.K_f: is_searching = True; search_text = ""
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: clicked = True

        if paused:
            action = draw_pause_menu(screen, clicked)
            if action == "resume": paused = False; pygame.time.delay(200)
            elif action == "restart": step = "MODE"; selected_p1 = -1; selected_p2 = -1; paused = False; pygame.time.delay(200)
            elif action == "quit": pygame.quit(); sys.exit()
            pygame.display.flip(); clock.tick(30); continue

        mouse_pos = pygame.mouse.get_pos()

        if step == "MODE":
            title = FONT_BIG.render("능력자 핑퐁 대전", True, WHITE)
            sub = FONT_TITLE.render("CONCEPT FIX VERSION", True, ACCENT_COLOR)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
            screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 250))
            btn_ai = pygame.Rect(SCREEN_WIDTH//2 - 350, 500, 200, 120)
            btn_pvp = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 120)
            btn_2vs2 = pygame.Rect(SCREEN_WIDTH//2 + 150, 500, 200, 120)
            buttons_ui = [(btn_ai, "1인용 (vs AI)", BLUE, "AI"), (btn_pvp, "2인용 (vs 친구)", RED, "PVP"), (btn_2vs2, "2vs2 (팀전)", PURPLE, "2VS2")]
            for btn, txt, color, mode in buttons_ui:
                c = color if btn.collidepoint(mouse_pos) else PANEL_BG
                pygame.draw.rect(screen, c, btn, border_radius=20)
                pygame.draw.rect(screen, WHITE, btn, 2, border_radius=20)
                t_surf = FONT_TITLE.render(txt, True, WHITE)
                if t_surf.get_width() > btn.width - 20:
                    t_surf = pygame.transform.scale(t_surf, (btn.width - 20, int(t_surf.get_height() * ((btn.width - 20) / t_surf.get_width()))))
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))
                if btn.collidepoint(mouse_pos) and clicked:
                    if SOUND_BUTTON: SOUND_BUTTON.play()
                    game_mode = mode; step = "P1"

        elif step == "DIFFICULTY":
            title = FONT_BIG.render("난이도 선택", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            diff_options = [("쉬움 (Easy)", GREEN, 0), ("보통 (Normal)", YELLOW, 1), ("어려움 (Hard)", ORANGE, 2), ("신 (God Mode)", RED, 3)]
            for i, (label, color, level) in enumerate(diff_options):
                btn_w, btn_h = 400, 80; btn_rect = pygame.Rect(SCREEN_WIDTH//2 - btn_w//2, 250 + i * 100, btn_w, btn_h)
                is_hover = btn_rect.collidepoint(mouse_pos)
                pygame.draw.rect(screen, color if is_hover else PANEL_BG, btn_rect, border_radius=15)
                pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)
                txt_surf = FONT_TITLE.render(label, True, BLACK if is_hover else color)
                screen.blit(txt_surf, (btn_rect.centerx - txt_surf.get_width()//2, btn_rect.centery - txt_surf.get_height()//2))
                if is_hover and clicked:
                    if SOUND_BUTTON: SOUND_BUTTON.play()
                    paddles.clear()
                    if game_mode == "2VS2":
                        p1 = Paddle(50, SCREEN_HEIGHT//4, is_ai=False, team=TEAM_1)
                        p1.ability_id = temp_p1_ability; p1.color = ABILITIES[temp_p1_ability].color
                        paddles.append(p1)
                        ai1 = Paddle(50, SCREEN_HEIGHT*3//4, is_ai=True, team=TEAM_1)
                        ai1.ability_id = selected_p2; ai1.color = ABILITIES[selected_p2].color; ai1.difficulty_level = level
                        paddles.append(ai1)
                        p2 = Paddle(SCREEN_WIDTH-70, SCREEN_HEIGHT//4, is_ai=True, team=TEAM_2)
                        p2_id = random.randint(0, 209)
                        p2.ability_id = p2_id; p2.color = ABILITIES.get(p2_id, ABILITIES[0]).color; p2.difficulty_level = level
                        paddles.append(p2)
                        ai2 = Paddle(SCREEN_WIDTH-70, SCREEN_HEIGHT*3//4, is_ai=True, team=TEAM_2)
                        ai2_id = random.randint(0, 209)
                        ai2.ability_id = ai2_id; ai2.color = ABILITIES.get(ai2_id, ABILITIES[0]).color; ai2.difficulty_level = level
                        paddles.append(ai2)
                    else:
                        p1 = Paddle(50, SCREEN_HEIGHT//2 - 50, is_ai=False, team=TEAM_1)
                        p1.ability_id = temp_p1_ability; p1.color = ABILITIES[temp_p1_ability].color
                        paddles.append(p1)
                        ai = Paddle(SCREEN_WIDTH - 70, SCREEN_HEIGHT//2 - 50, is_ai=True, team=TEAM_2)
                        ai.difficulty_level = level; ai_id = random.randint(0, 209)
                        ai.ability_id = ai_id; ai.color = ABILITIES.get(ai_id, ABILITIES[0]).color
                        paddles.append(ai)
                    reset_game_state(); return "GAME"

        elif step in ["P1", "P2"]:
            target = "플레이어 1" if step == "P1" else "플레이어 2"
            if game_mode == "2VS2" and step == "P2": target = "나의 동료 (AI)"

            search_rect = pygame.Rect(SCREEN_WIDTH - 350, 30, 300, 40)
            pygame.draw.rect(screen, SEARCH_BG if not is_searching else ACCENT_COLOR, search_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, search_rect, 2, border_radius=10)
            prompt = search_text if search_text else "영웅 검색 (F키)"
            screen.blit(FONT_UI.render(prompt, True, WHITE if search_text else GRAY), (search_rect.x + 10, search_rect.y + 10))

            list_area = pygame.Rect(30, 90, 800, SCREEN_HEIGHT - 120)
            pygame.draw.rect(screen, PANEL_BG, list_area, border_radius=15)
            total_pages = math.ceil(len(filtered_ids) / per_page) if filtered_ids else 1
            if current_page >= total_pages: current_page = 0

            screen.blit(FONT_TITLE.render(f"{target} 선택 ({len(filtered_ids)}명 검색됨)", True, WHITE), (40, 40))
            screen.blit(FONT_UI.render(f"Page {current_page+1}/{total_pages}", True, GRAY), (700, 60))

            start_i = current_page * per_page; end_i = min((current_page + 1) * per_page, len(filtered_ids))
            cols = 5; btn_w, btn_h = 140, 65; margin_x = 15; margin_y = 15
            start_x, start_y = list_area.x + 20, list_area.y + 20
            current_selection = selected_p1 if step == "P1" else selected_p2

            for idx in range(start_i, end_i):
                real_id = filtered_ids[idx]; r_idx = idx - start_i
                col = r_idx % cols; row = r_idx // cols
                x = start_x + col * (btn_w + margin_x); y = start_y + row * (btn_h + margin_y)
                rect = pygame.Rect(x, y, btn_w, btn_h)
                is_hover = rect.collidepoint(mouse_pos)
                if is_hover and clicked:
                    if SOUND_BUTTON: SOUND_BUTTON.play()
                    if step == "P1": selected_p1 = real_id
                    else: selected_p2 = real_id
                bg_c = ABILITIES[real_id].color if real_id == current_selection else DARK_GRAY
                if is_hover and real_id != current_selection: bg_c = GRAY
                pygame.draw.rect(screen, bg_c, rect, border_radius=8)
                if real_id == current_selection: pygame.draw.rect(screen, WHITE, rect, 3, border_radius=8)
                name_surf = FONT_UI.render(ABILITIES[real_id].name, True, WHITE if bg_c != WHITE else BLACK)
                screen.blit(name_surf, name_surf.get_rect(center=rect.center))

            info_area = pygame.Rect(850, 90, 330, SCREEN_HEIGHT - 120)
            pygame.draw.rect(screen, PANEL_BG, info_area, border_radius=15)

            if current_selection != -1:
                ab = ABILITIES[current_selection]
                # 능력 색상 테두리 (펄스)
                now_ms = pygame.time.get_ticks()
                pulse = int(abs(math.sin(now_ms * 0.004)) * 30)
                bc = (min(255, ab.color[0]+pulse), min(255, ab.color[1]+pulse), min(255, ab.color[2]+pulse))
                pygame.draw.rect(screen, bc, info_area, 3, border_radius=15)

                screen.blit(FONT_TITLE.render(ab.name, True, ab.color), (870, 110))
                screen.blit(FONT_FLAVOR.render(f'"{ab.flavor}"', True, SILVER), (870, 155))
                dur_surf = FONT_UI.render(get_skill_duration(current_selection), True, MINT)
                screen.blit(dur_surf, (870, 180))
                pygame.draw.line(screen, GRAY, (870, 205), (1160, 205), 1)

                # 스킬 설명
                lines = ab.desc.split('\n'); ly = 218
                for line in lines:
                    c = WHITE; f = FONT_DESC
                    if line.startswith('['): c = YELLOW; f = FONT_MAIN; ly += 8
                    screen.blit(f.render(line, True, c), (870, ly)); ly += 28

                # ── 미리보기 파티클 애니메이션 ──
                preview_cx = 1010
                preview_cy = min(ly + 60, SCREEN_HEIGHT - 120)
                preview_r  = 35

                # 능력 컨셉에 따른 미리보기 이펙트
                pv_t = now_ms * 0.003
                if current_selection in [0,20,39,41,109,159,186]:
                    # 화염 원
                    for i in range(8):
                        a = pv_t + i * math.pi / 4
                        px = preview_cx + int(math.cos(a) * preview_r)
                        py = preview_cy + int(math.sin(a) * preview_r)
                        r_col = (255, max(0, 80 - i*8), 0)
                        pygame.draw.circle(screen, r_col, (px, py), 5 - i//2)
                elif current_selection in [1,114,160]:
                    # 얼음 결정
                    for i in range(6):
                        a = pv_t * 0.3 + i * math.pi / 3
                        for r_off in [15, 28, 38]:
                            px = preview_cx + int(math.cos(a) * r_off)
                            py = preview_cy + int(math.sin(a) * r_off)
                            pygame.draw.circle(screen, CYAN, (px, py), 3)
                elif current_selection in [4,135,161,203]:
                    # 시계 회전
                    pygame.draw.circle(screen, GRAY, (preview_cx, preview_cy), preview_r, 2)
                    hand_x = preview_cx + int(math.cos(pv_t * 2) * (preview_r-8))
                    hand_y = preview_cy + int(math.sin(pv_t * 2) * (preview_r-8))
                    pygame.draw.line(screen, PURPLE, (preview_cx, preview_cy), (hand_x, hand_y), 3)
                elif current_selection in [12,44,120,127,158]:
                    # 자력선
                    for i in range(5):
                        a = pv_t + i * math.pi * 2 / 5
                        for t2 in [0.3, 0.6, 1.0]:
                            px = preview_cx + int(math.cos(a) * preview_r * t2)
                            py = preview_cy + int(math.sin(a) * preview_r * t2)
                            pygame.draw.circle(screen, MAGENTA, (px, py), 2)
                elif current_selection in [7,54,98,133,163]:
                    # 투명 페이드
                    fade_alpha = int(abs(math.sin(pv_t)) * 200)
                    ghost = pygame.Surface((preview_r*2, preview_r*2), pygame.SRCALPHA)
                    pygame.draw.circle(ghost, (*GRAY, fade_alpha), (preview_r, preview_r), preview_r)
                    screen.blit(ghost, (preview_cx - preview_r, preview_cy - preview_r))
                elif current_selection in [35,100]:
                    # 번개
                    for i in range(4):
                        a = pv_t * 3 + i * math.pi / 2
                        pts = []
                        for s in range(5):
                            px = preview_cx + int(math.cos(a + s*0.3) * (preview_r * s / 4))
                            py = preview_cy + int(math.sin(a + s*0.3) * (preview_r * s / 4))
                            pts.append((px, py))
                        if len(pts) > 1: pygame.draw.lines(screen, YELLOW, False, pts, 2)
                elif current_selection in [16,52,205]:
                    # 중력 소용돌이
                    for i in range(20):
                        t3 = pv_t + i * 0.3
                        r_off = preview_r * (1 - i/20)
                        px = preview_cx + int(math.cos(t3) * r_off)
                        py = preview_cy + int(math.sin(t3) * r_off)
                        pygame.draw.circle(screen, NAVY, (px, py), 3)
                else:
                    # 기본 회전 원
                    for i in range(6):
                        a = pv_t + i * math.pi / 3
                        px = preview_cx + int(math.cos(a) * preview_r)
                        py = preview_cy + int(math.sin(a) * preview_r)
                        pygame.draw.circle(screen, ab.color, (px, py), 5)
                    pygame.draw.circle(screen, ab.color, (preview_cx, preview_cy), 12, 2)

                # 미리보기 라벨
                pv_label = FONT_UI.render("미리보기", True, GRAY)
                screen.blit(pv_label, (preview_cx - pv_label.get_width()//2, preview_cy + preview_r + 8))

            btn_prev = pygame.Rect(50, SCREEN_HEIGHT-80, 100, 50)
            btn_next = pygame.Rect(170, SCREEN_HEIGHT-80, 100, 50)
            btn_ok = pygame.Rect(SCREEN_WIDTH-250, SCREEN_HEIGHT-90, 200, 60)
            pygame.draw.rect(screen, DARK_GRAY, btn_prev, border_radius=10); screen.blit(FONT_UI.render("< 이전", True, WHITE), (75, SCREEN_HEIGHT-65))
            pygame.draw.rect(screen, DARK_GRAY, btn_next, border_radius=10); screen.blit(FONT_UI.render("다음 >", True, WHITE), (195, SCREEN_HEIGHT-65))
            ok_color = ACCENT_COLOR if current_selection != -1 else GRAY
            pygame.draw.rect(screen, ok_color, btn_ok, border_radius=15)
            screen.blit(FONT_TITLE.render("결정", True, BLACK), (btn_ok.centerx-30, btn_ok.centery-20))

            if clicked:
                if btn_prev.collidepoint(mouse_pos) and current_page > 0:
                    if SOUND_BUTTON: SOUND_BUTTON.play(); current_page -= 1
                if btn_next.collidepoint(mouse_pos) and current_page < total_pages - 1:
                    if SOUND_BUTTON: SOUND_BUTTON.play(); current_page += 1
                if btn_ok.collidepoint(mouse_pos) and current_selection != -1:
                    if SOUND_BUTTON: SOUND_BUTTON.play()
                    if step == "P1":
                        temp_p1_ability = selected_p1
                        if game_mode == "2VS2": step = "P2"; current_page = 0; filtered_ids = list(ABILITIES.keys()); search_text = ""
                        elif game_mode == "AI": step = "DIFFICULTY"
                        else: step = "P2"; current_page = 0; filtered_ids = list(ABILITIES.keys()); search_text = ""
                    elif step == "P2":
                        if game_mode == "2VS2": step = "DIFFICULTY"
                        else:
                            paddles.clear()
                            p1 = Paddle(50, SCREEN_HEIGHT//2 - 50, is_ai=False, team=TEAM_1)
                            p1.ability_id = temp_p1_ability; p1.color = ABILITIES[temp_p1_ability].color
                            paddles.append(p1)
                            p2 = Paddle(SCREEN_WIDTH-70, SCREEN_HEIGHT//2 - 50, is_ai=False, team=TEAM_2)
                            p2.ability_id = selected_p2; p2.color = ABILITIES[selected_p2].color
                            paddles.append(p2)
                            reset_game_state(); return "GAME"

        pygame.display.flip(); clock.tick(30)

def scene_game():
    running = True; paused = False; SHOW_BALL_EVENT = pygame.USEREVENT + 1
    global score_team1, score_team2
    while running:
        clicked = False; shake_x, shake_y = shake_effect.get_offset()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m: paused = not paused
                if not paused:
                    if len(paddles) > 0 and not paddles[0].is_ai:
                        if event.key == pygame.K_e: use_ability(paddles[0], "BASIC", ball)
                        elif event.key == pygame.K_q: use_ability(paddles[0], "SKILL", ball)
                        elif event.key == pygame.K_SPACE: use_ability(paddles[0], "ULT", ball)
                    p2_idx = 2 if game_mode == "2VS2" else 1
                    if len(paddles) > p2_idx and not paddles[p2_idx].is_ai:
                        if event.key == pygame.K_SLASH: use_ability(paddles[p2_idx], "BASIC", ball)
                        elif event.key == pygame.K_PERIOD: use_ability(paddles[p2_idx], "SKILL", ball)
                        elif event.key == pygame.K_RETURN: use_ability(paddles[p2_idx], "ULT", ball)
            if event.type == SHOW_BALL_EVENT: ball.visible = True; pygame.time.set_timer(SHOW_BALL_EVENT, 0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: clicked = True

        if paused:
            action = draw_pause_menu(screen, clicked)
            if action == "resume": paused = False; pygame.time.delay(200)
            elif action == "restart": return "SELECT"
            elif action == "quit": pygame.quit(); sys.exit()
            pygame.display.flip(); clock.tick(60); continue

        keys = pygame.key.get_pressed()
        if len(paddles) > 0 and not paddles[0].is_ai:
            paddles[0].move_manual(keys[pygame.K_w], keys[pygame.K_s])
        p2_idx = 2 if game_mode == "2VS2" else 1
        if len(paddles) > p2_idx and not paddles[p2_idx].is_ai:
            paddles[p2_idx].move_manual(keys[pygame.K_UP], keys[pygame.K_DOWN])

        rem = ball.move()
        if rem == "REMOVE": ball.reset(1)

        # 환경 이벤트 업데이트
        update_field_event(ball)

        for fb in fake_balls[:]:
            res = fb.move()
            if res == "REMOVE": fake_balls.remove(fb)
            elif fb.rect.left < 0 or fb.rect.right > SCREEN_WIDTH: fake_balls.remove(fb)

        if ball.timers['sticky'] > 0 and pygame.time.get_ticks() > ball.timers['sticky']:
            target = ball.sticky_target; ball.sticky_target = None
            if target:
                if target.rect.centerx < SCREEN_WIDTH // 2:
                    ball.rect.left = target.rect.right + 5; ball.speed_x = 15
                else:
                    ball.rect.right = target.rect.left - 5; ball.speed_x = -15
            else:
                ball.speed_x = 15 if ball.rect.centerx < SCREEN_WIDTH//2 else -15
            ball.speed_y = random.choice([-10, 10]); ball.timers['sticky'] = 0

        for p in paddles[:]:
            if p.is_expired():
                paddles.remove(p); spawn_particles(p.rect.centerx, p.rect.centery, p.color, 20, p_type="IMPLODE"); continue
            p.update(ball)

        for obs in obstacles[:]:
            if obs.is_expired(): obstacles.remove(obs)

        for p in paddles:
            if ball.rect.colliderect(p.rect):
                if SOUND_PONG: SOUND_PONG.play()
                now = pygame.time.get_ticks()
                if ball.timers['fire'] > now: p.apply_effect('burn', 2000)
                if ball.timers['poison'] > now: p.apply_effect('poison', 3000)
                if p.team == TEAM_1:
                    ball.speed_x = abs(ball.speed_x) + 0.2; ball.rect.left = p.rect.right
                    ball.last_hit_team = TEAM_1
                else:
                    ball.speed_x = -(abs(ball.speed_x) + 0.2); ball.rect.right = p.rect.left
                    ball.last_hit_team = TEAM_2
                # 리코셰: 패들 반사 시 bounce_count 초기화
                if p.ability_id == 208: ball.bounce_count = 0
                # 성직자: 칠 때마다 가속
                if p.ability_id == 156: ball.speed_x *= 1.15; spawn_particles(p.rect.centerx, p.rect.centery, GOLD, 5, p_type="STAR")
                spawn_particles(ball.rect.centerx, ball.rect.centery, WHITE, count=5, p_type="SHOCKWAVE")

        for fb in fake_balls[:]:
            for p in paddles:
                if fb.rect.colliderect(p.rect):
                    fake_balls.remove(fb); spawn_particles(fb.rect.centerx, fb.rect.centery, fb.color, count=5, p_type="EXPLODE"); break

        if ball.rect.left <= 0:
            saved = False
            for p in [pad for pad in paddles if pad.team == TEAM_1]:
                if pygame.time.get_ticks() < p.timers['revive']:
                    ball.speed_x = abs(ball.speed_x) * 1.5
                    spawn_text(p.rect.centerx, p.rect.centery, "SAVE!", (50, 0, 50)); p.timers['revive'] = 0; saved = True; break
            if not saved:
                score_team2 += 1
                shake_effect.start(25, 12)
                spawn_center_effect(f"TEAM 2  {score_team2} POINT!", RED)
                # 득점 폭발 파티클
                for _ in range(3):
                    spawn_particles(random.randint(0, SCREEN_WIDTH//2), random.randint(100, SCREEN_HEIGHT-100),
                                    RED, count=15, speed=6, p_type="STAR")
                reset_round()

        if ball.rect.right >= SCREEN_WIDTH:
            saved = False
            for p in [pad for pad in paddles if pad.team == TEAM_2]:
                if pygame.time.get_ticks() < p.timers['revive']:
                    ball.speed_x = -abs(ball.speed_x) * 1.5
                    spawn_text(p.rect.centerx, p.rect.centery, "SAVE!", (50, 0, 50)); p.timers['revive'] = 0; saved = True; break
            if not saved:
                score_team1 += 1
                shake_effect.start(25, 12)
                spawn_center_effect(f"TEAM 1  {score_team1} POINT!", GREEN)
                for _ in range(3):
                    spawn_particles(random.randint(SCREEN_WIDTH//2, SCREEN_WIDTH), random.randint(100, SCREEN_HEIGHT-100),
                                    GREEN, count=15, speed=6, p_type="STAR")
                reset_round()

        if score_team1 >= MAX_SCORE or score_team2 >= MAX_SCORE: return "GAMEOVER"

        display_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        display_surf.fill(BG_COLOR)

        # 환경 이벤트에 따른 배경 색조
        if field_event == 'heatwave':
            display_surf.fill((30, 15, 10))
        elif field_event == 'flood':
            display_surf.fill((10, 18, 35))
        elif field_event == 'timewarp':
            display_surf.fill((18, 10, 30))

        if ball.timers['guide'] > pygame.time.get_ticks(): draw_trajectory(display_surf, ball)

        for p in particles[:]: p.update(); p.draw(display_surf)
        for obs in obstacles: obs.draw(display_surf)
        pygame.draw.aaline(display_surf, GRAY, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT))
        for p in paddles: p.draw(display_surf)
        ball.draw(display_surf)
        for fb in fake_balls: fb.draw(display_surf)

        # 환경 이벤트 오버레이 (패들/공 위에 그려짐)
        draw_field_event_overlay(display_surf)

        for t in floating_texts[:]: t.update(); t.draw(display_surf)
        for ce in central_effects[:]: ce.update(); ce.draw(display_surf)

        particles[:] = [p for p in particles if p.life > 0]
        floating_texts[:] = [t for t in floating_texts if t.life > 0]
        central_effects[:] = [c for c in central_effects if c.life > 0]

        # --- 점수 ---
        score_txt = FONT_TITLE.render(f"{score_team1}  :  {score_team2}", True, WHITE)
        display_surf.blit(score_txt, (SCREEN_WIDTH//2 - score_txt.get_width()//2, 20))

        # --- 캐릭터 이름 (상단) ---
        if len(paddles) > 0 and paddles[0].ability_id in ABILITIES:
            p1_ab = ABILITIES[paddles[0].ability_id]
            p_name = FONT_TITLE.render(f"P1: {p1_ab.name}", True, p1_ab.color)
            display_surf.blit(p_name, (50, 20))

        p2_idx = 2 if game_mode == "2VS2" else 1
        if len(paddles) > p2_idx and paddles[p2_idx].ability_id in ABILITIES:
            p2_ab = ABILITIES[paddles[p2_idx].ability_id]
            p2_label = "AI" if paddles[p2_idx].is_ai else "P2"
            p2_name = FONT_TITLE.render(f"{p2_label}: {p2_ab.name}", True, p2_ab.color)
            display_surf.blit(p2_name, (SCREEN_WIDTH - p2_name.get_width() - 50, 20))

        # --- HUD (스킬 이름 + 쿨다운) ---
        if len(paddles) > 0 and not paddles[0].is_ai:
            draw_hud(display_surf, paddles[0], is_left=True)
        if len(paddles) > p2_idx and not paddles[p2_idx].is_ai:
            draw_hud(display_surf, paddles[p2_idx], is_left=False)

        # --- 조작 가이드 ---
        guide = "P1: W/S 이동 | E 강타 | Q 스킬 | Space 궁극기"
        display_surf.blit(FONT_DESC.render(guide, True, GRAY), (50, 70))

        screen.blit(display_surf, (shake_x, shake_y))
        pygame.display.flip(); clock.tick(60)

def scene_gameover():
    global score_team1, score_team2
    # 파티클 폭죽 타이머
    firework_timer = 0
    while True:
        now = pygame.time.get_ticks()
        screen.fill(BG_COLOR)

        if game_mode == "2VS2": w_text = "TEAM 1 WIN!" if score_team1 >= MAX_SCORE else "TEAM 2 WIN!"
        else: w_text = "P1 WIN!" if score_team1 >= MAX_SCORE else ("AI WIN!" if game_mode == "AI" else "P2 WIN!")
        color = GREEN if score_team1 >= MAX_SCORE else RED

        # 배경 파티클 폭죽
        if now > firework_timer:
            firework_timer = now + 600
            cx = random.randint(100, SCREEN_WIDTH-100)
            cy = random.randint(100, SCREEN_HEIGHT-200)
            fc = random.choice([RED, GREEN, YELLOW, CYAN, PURPLE, ORANGE, PINK])
            spawn_particles(cx, cy, fc, count=20, speed=5, p_type="STAR")
        for p in particles[:]: p.update(); p.draw(screen)
        particles[:] = [p for p in particles if p.life > 0]

        # 승리 텍스트 (펄스)
        pulse_scale = 1.0 + math.sin(now * 0.004) * 0.06
        base_surf = FONT_BIG.render(w_text, True, color)
        pw = int(base_surf.get_width() * pulse_scale)
        ph = int(base_surf.get_height() * pulse_scale)
        if pw > 0 and ph > 0:
            scaled = pygame.transform.scale(base_surf, (pw, ph))
            shadow = pygame.transform.scale(FONT_BIG.render(w_text, True, BLACK), (pw, ph))
            shadow.set_alpha(120)
            screen.blit(shadow, (SCREEN_WIDTH//2 - pw//2 + 5, SCREEN_HEIGHT//2 - 130 + 5))
            screen.blit(scaled, (SCREEN_WIDTH//2 - pw//2, SCREEN_HEIGHT//2 - 130))

        # 최종 스코어
        score_surf = FONT_TITLE.render(f"{score_team1}  :  {score_team2}", True, WHITE)
        screen.blit(score_surf, (SCREEN_WIDTH//2 - score_surf.get_width()//2, SCREEN_HEIGHT//2 - 30))

        # 안내 텍스트
        sub = FONT_TITLE.render("Space → 타이틀 / R → 재경기", True, GRAY)
        screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 50))

        # 캐릭터 매치업 표시
        if len(paddles) >= 2:
            p1_ab = ABILITIES.get(paddles[0].ability_id)
            p2_ab = ABILITIES.get(paddles[min(1, len(paddles)-1)].ability_id)
            if p1_ab and p2_ab:
                vs_surf = FONT_MAIN.render(f"{p1_ab.name}  vs  {p2_ab.name}", True, GRAY)
                screen.blit(vs_surf, (SCREEN_WIDTH//2 - vs_surf.get_width()//2, SCREEN_HEIGHT//2 + 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return "SELECT"
                if event.key == pygame.K_r:
                    reset_game_state(); return "GAME"
        pygame.display.flip(); clock.tick(60)

def main():
    current_state = "SELECT"
    try:
        while True:
            if current_state == "SELECT": current_state = scene_selection()
            elif current_state == "GAME": current_state = scene_game()
            elif current_state == "GAMEOVER": current_state = scene_gameover()
    except Exception as e:
        print("오류:", e); traceback.print_exc()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()