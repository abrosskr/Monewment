import numpy as np
from scipy.optimize import lsq_linear

# 1. 잉크 카트리지 정의 (The Elements)
# 각 잉크 1ml가 가진 맛의 벡터 [Salty, Sweet, Umami, Spicy, Sour]
INKS = {
    "Water":       np.array([0.0, 0.0, 0.0, 0.0, 0.0]), # 희석용
    "Soy_Base":    np.array([5.0, 0.2, 2.0, 0.0, 0.1]), # 짠맛+감칠맛
    "Sugar_Syrup": np.array([0.0, 8.0, 0.0, 0.0, 0.0]), # 단맛
    "Vinegar":     np.array([0.0, 0.2, 0.0, 0.0, 5.0]), # 신맛
    "MSG_Sol":     np.array([0.5, 0.0, 10.0, 0.0, 0.0]), # 감칠맛 폭탄
    "Capsaicin":   np.array([0.0, 0.0, 0.0, 50.0, 0.0]), # 매운맛 폭탄
}

INK_NAMES = list(INKS.keys())
INK_MATRIX = np.array([INKS[name] for name in INK_NAMES]).T  # (Flavor Dimension x Ink Count)

def solve_recipe(target_vector):
    """
    Target Vector [Salt, Sweet, Umami, Spicy, Sour]를 만들기 위한
    최적의 잉크 용량(ml)을 계산합니다.
    """
    print(f"\n🎯 Target Taste: {target_vector}")
    
    # 제약 조건: 잉크 양은 0 이상이어야 함 (Lower bound = 0)
    # lsq_linear: ||Ax - b||^2 를 최소화하는 x를 찾음 (Least Squares)
    res = lsq_linear(INK_MATRIX, target_vector, bounds=(0, np.inf))
    
    if not res.success:
        print("❌ 배합 실패: 최적해를 찾을 수 없습니다.")
        return

    amounts = res.x
    
    print("🧪 Calculated Ink Recipe:")
    for name, ml in zip(INK_NAMES, amounts):
        if ml > 0.01: # 0.01ml 이상만 출력
            print(f"  - {name}: {ml:.2f} ml")
            
    # 검증
    actual_taste = INK_MATRIX @ amounts
    print(f"✅ Simulated Result: {actual_taste}")
    error = np.linalg.norm(target_vector - actual_taste)
    print(f"📉 Error Rate: {error:.4f}")

if __name__ == "__main__":
    # 시나리오 1: 달콤 짭짤한 불고기 소스
    # Salt: 10, Sweet: 8, Umami: 5, Spicy: 0, Sour: 0
    target_bulgogi = np.array([10.0, 8.0, 5.0, 0.0, 0.0])
    solve_recipe(target_bulgogi)

    # 시나리오 2: 매운 냉면 육수
    # Salt: 5, Sweet: 8, Umami: 8, Spicy: 25, Sour: 10
    target_naengmyeon = np.array([5.0, 8.0, 8.0, 25.0, 10.0])
    solve_recipe(target_naengmyeon)
