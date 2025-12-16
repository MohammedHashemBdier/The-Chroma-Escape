from model import GameState

class Heuristics:
    @staticmethod
    def h1_remaining_blocks(state: GameState) -> float:
        """
        الهيوريستك الأول: عدد القطع المتبقية مضروباً بوزن
        h(n) = عدد القطع المتبقية * 10
        
        هذا هيوريستك بسيط وقبول admissible لأن كل قطعة يجب أن تخرج من اللعبة
        """
        return float(len(state.blocks) * 10)

    @staticmethod
    def h2_manhattan_distance(state: GameState) -> float:
        """
        الهيوريستك الثاني: مسافة مانهاتن من القطع إلى أقرب مخرج
        h(n) = مجموع المسافات المانهاتن من كل قطعة إلى أقرب مخرج من نفس اللون
        
        هذا هيوريستك admissible لأنه يحسب الحد الأدنى من الحركات المطلوبة
        """
        if state.check_win_condition():
            return 0.0
        
        total_distance = 0.0
        for block in state.blocks:
            min_distance = float('inf')
            for (exit_x, exit_y), exit_info in state.board.exits.items():
                if exit_info.get("color", "").lower() == block.color.lower():
                    distance = abs(block.x - exit_x) + abs(block.y - exit_y)
                    min_distance = min(min_distance, distance)
            
            if min_distance != float('inf'):
                total_distance += min_distance
        
        return total_distance

    @staticmethod
    def h3_combined(state: GameState) -> float:
        """
        الهيوريستك الثالث: مزيج من عدد القطع والمسافة
        h(n) = (عدد القطع * 5) + (مسافة مانهاتن * 0.5)
        
        هذا يعطي أهمية أكبر لإخراج القطع مع الأخذ في الاعتبار المسافة
        """
        if state.check_win_condition():
            return 0.0
        
        remaining_blocks_cost = len(state.blocks) * 5
        manhattan_cost = Heuristics.h2_manhattan_distance(state) * 0.5
        
        return remaining_blocks_cost + manhattan_cost

    @staticmethod
    def h4_blocks_with_distance_weighted(state: GameState) -> float:
        """
        الهيوريستك الرابع: متوسط المسافة لكل قطعة + عدد القطع
        h(n) = (عدد القطع * 10) + (متوسط المسافة * 2)
        
        يعتبر المسافة النسبية لكل قطعة بشكل منفصل
        """
        if state.check_win_condition():
            return 0.0
        
        remaining_blocks_cost = len(state.blocks) * 10
        
        if not state.blocks:
            return remaining_blocks_cost
        
        total_distance = Heuristics.h2_manhattan_distance(state)
        avg_distance = total_distance / max(len(state.blocks), 1)
        
        return remaining_blocks_cost + avg_distance * 2

    @staticmethod
    def h5_trapped_blocks_penalty(state: GameState) -> float:
        """
        الهيوريستك الخامس: مع عقوبة للقطع المحاصرة
        h(n) = (عدد القطع * 10) + (عدد القطع المحاصرة * 50)
        
        يعطي عقوبة أكبر للحالات التي فيها قطع محاصرة (غير قابلة للحركة)
        """
        remaining_blocks_cost = len(state.blocks) * 10
        trapped_blocks = len(state.get_trapped_block_indices())
        trapped_penalty = trapped_blocks * 50
        
        return float(remaining_blocks_cost + trapped_penalty)

    @staticmethod
    def zero_heuristic(state: GameState) -> float:
        """
        هيوريستك صفري - يستخدم عندما نريد غونيفورم كوست سيرتش (UCS)
        """
        return 0.0
