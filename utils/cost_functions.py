from model import GameState

class CostFunctions:
    """
    COST (التكلفة) في خوارزميات البحث:
    الكوست هو المسافة من الحالة الأولية إلى الحالة الحالية
    بمعنى: كم عدد الخطوات/الحركات اللي عملناها للوصول لهاي الحالة
    
    الكوست يستخدم في:
    - UCS (Uniform Cost Search): يختار الحالة مع أقل كوست
    - A* Search: f(n) = g(n) + h(n)  حيث g(n) هو الكوست
    """
    
    @staticmethod
    def uniform_cost(state: GameState) -> float:
        """
        كوست موحد: كل حركة تكلف 1
        g(n) = عدد الخطوات من الحالة الأولية إلى الحالة الحالية
        
        يستخدم في BFS و Uniform Cost Search
        """
        return float(state.depth)

    @staticmethod
    def exit_bonus_cost(state: GameState) -> float:
        """
        كوست مع مكافأة على إخراج القطع:
        - كل حركة عادية = 1
        - كل حركة خروج = 0.5 (نقل أقل للحركات التي تنهي القطع)
        
        هذا يشجع الخوارزمية على الأولوية لحركات الخروج
        """
        cost = float(state.depth)
        
        initial_blocks = 0
        current = state
        while current.parent is not None:
            current = current.parent
        
        initial_blocks_count = current.move_count if hasattr(current, 'move_count') else 0
        blocks_exited = initial_blocks_count - len(state.blocks)
        
        bonus = blocks_exited * 0.5
        
        return max(0.0, cost - bonus)

    @staticmethod
    def minimum_spanning_cost(state: GameState) -> float:
        """
        كوست بناءً على الحد الأدنى من الحركات المتوقعة:
        تحسب الحد الأدنى النظري من الحركات المطلوبة
        g(n) = كوست حقيقي (عمق في البحث)
        """
        return float(state.depth)

    @staticmethod
    def move_penalty_cost(state: GameState) -> float:
        """
        كوست مع عقوبة إضافية للحالات البعيدة:
        يضيف عقوبة صغيرة للحركات البعيدة عن الهدف
        g(n) = العمق + (عدد القطع المتبقية * 0.1)
        
        هذا يحفز الخوارزمية على إخراج القطع بسرعة
        """
        base_cost = float(state.depth)
        remaining_blocks_penalty = len(state.blocks) * 0.1
        return base_cost + remaining_blocks_penalty

    @staticmethod
    def adaptive_cost(state: GameState, initial_blocks_count: int) -> float:
        """
        كوست تكيفي يتغير بناءً على التقدم:
        - في البداية: كوست عالي
        - مع كل قطعة تخرج: كوست ينخفض
        
        g(n) = العمق / (1 + عدد القطع المخرجة)
        """
        blocks_exited = initial_blocks_count - len(state.blocks)
        denominator = 1.0 + blocks_exited
        return float(state.depth) / denominator

    @staticmethod
    def get_initial_blocks_count(state: GameState) -> int:
        """
        الحصول على عدد القطع الأولية (في الحالة الأولية)
        """
        current = state
        while current.parent is not None:
            current = current.parent
        return len(current.blocks)
