import numpy as np
import sympy as sp
from sympy import Interval, EmptySet
from sympy.core import numbers
from sympy.sets import FiniteSet
from fractions import Fraction
import math

class IntervalNaturalExtention:
    def __init__(self):
        self.inf = float("inf")

    def eval_interval_expr(self, expr, interval_dict):
        """
        Рекурсивно вычисляет выражение, где переменные заменены на интервалы.
        :param expr: SymPy-выражение.
        :param interval_dict: Словарь, где ключи — переменные, а значения — интервалы или числа.
        :return: Результат вычисления (интервал или число).
        """
        if isinstance(expr, sp.Symbol):
            # Если это переменная, заменяем её на интервал из словаря
            return interval_dict.get(expr, expr)  # Если переменной нет в словаре, возвращаем её как есть

        elif isinstance(expr, numbers.Half):    # Если это "Половина", 1/2
            return expr

        elif isinstance(expr, FiniteSet):   # Если это вырожденный интервал
            return expr.args[0]

        elif isinstance(expr, sp.Add):  # Обработка сложения
            intervals = [self.eval_interval_expr(arg, interval_dict) for arg in expr.args if arg != EmptySet]
            return self.__interval_add(*intervals)

        elif isinstance(expr, sp.Mul):  # Обработка умножения
            intervals = [self.eval_interval_expr(arg, interval_dict) for arg in expr.args if arg != EmptySet]
            return self.__interval_mul(*intervals)

        elif isinstance(expr, sp.Pow):  # Обработка степени
            base = self.eval_interval_expr(expr.base, interval_dict)
            exponent = self.eval_interval_expr(expr.exp, interval_dict)
            return self.__interval_pow(base, exponent)

        elif isinstance(expr, sp.sin):  # Обработка синуса
            arg = self.eval_interval_expr(expr.args[0], interval_dict)
            return self.__interval_sin(arg)

        elif isinstance(expr, sp.cos):  # Обработка косинуса
            arg = self.eval_interval_expr(expr.args[0], interval_dict)
            return self.__interval_cos(arg)

        elif isinstance(expr, sp.exp):  # Обработка экспоненты
            arg = self.eval_interval_expr(expr.args[0], interval_dict)
            return self.__interval_exp(arg)

        else:   # Если это число, возвращаем как есть
            return expr


    def __interval_add(self, *intervals):
        """
        Сложение интервалов.
        """
        intervals = [i for i in intervals if i != EmptySet]
        result_start = sum(i.start if isinstance(i, Interval) else i for i in intervals)
        result_end = sum(i.end if isinstance(i, Interval) else i for i in intervals)

        if result_start == result_end:
            return result_start
        else:
            return Interval(result_start, result_end)


    def __interval_mul(self, *intervals):
        """
        Умножение интервалов.
        """
        intervals = [i for i in intervals if i != EmptySet]
        first = intervals[0]
        result_start = min(first.start, first.end) if isinstance(first, Interval) else first
        result_end = max(first.start, first.end) if isinstance(first, Interval) else first

        for i in range(1, len(intervals)):
            val = intervals[i]
            if isinstance(val, Interval):
                result_start = min(result_start * val.start, result_start * val.end)
                result_end = max(result_end * val.start, result_end * val.end)
            else:
                result_start *= val
                result_end *= val

        if result_start == result_end:
            return result_start
        else:
            return Interval(min(result_start, result_end), max(result_start, result_end))


    def __real_pow(self, x, exponent):
        """
        Вычисляет действительное значение x^exponent.
        """
        ordinary_fraction = Fraction(exponent).limit_denominator()
        denominator = ordinary_fraction.denominator
        if denominator != 1 and x < 0:
            return -abs(x) ** exponent
        else:
            return x ** exponent

    def __interval_pow(self, base, exponent):
        """
        Возведение интервала в степень.
        """
        if isinstance(base, Interval):
            exponent_float = float(exponent)
            ordinary_fraction = Fraction(exponent_float).limit_denominator()
            numenator = ordinary_fraction.numerator
            denominator = ordinary_fraction.denominator

            if exponent_float > 0:
                if denominator % 2 == 0:
                    if base.start >= 0:
                        return Interval(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float))
                    else:
                        return None
                else:
                    if numenator % 2 == 0:
                        if base.end < 0 or base.start > 0:
                            return Interval(min(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)), max(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)))
                        else:
                            return Interval(0, max(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)))
                    else:
                        return Interval(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float))
            else:
                if denominator % 2 == 0:
                    if base.end <= 0:
                        return None
                    elif base.start == 0:
                        return Interval(self.__real_pow(base.end, exponent_float), self.inf)
                    else:
                        return Interval(self.__real_pow(base.end, exponent_float), self.__real_pow(base.start, exponent_float))
                else:
                    if numenator % 2 == 0:
                        if base.end < 0 or base.start > 0:
                            return Interval(min(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)), max(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)))
                        elif base.start == 0:
                            return Interval(self.__real_pow(base.end, exponent_float), self.inf)
                        elif base.end == 0:
                            return Interval(self.__real_pow(base.start, exponent_float), self.inf)
                        else:
                            return Interval(min(self.__real_pow(base.start, exponent_float), self.__real_pow(base.end, exponent_float)), self.inf)
                    else:
                        if base.end < 0 or base.start > 0:
                            return Interval(self.__real_pow(base.end, exponent_float), self.__real_pow(base.start, exponent_float))
                        elif base.start == 0:
                            return Interval(self.__real_pow(base.end, exponent_float), self.inf)
                        elif base.end == 0:
                            return Interval(-self.inf, self.__real_pow(base.start, exponent_float))
                        else:
                            return Interval(-self.inf, self.inf)
        else:
            return float(base**exponent)


    def __interval_sin(self, arg):
        """
        Вычисление синуса для интервала.
        """
        if isinstance(arg, Interval):
            if self.__check_a_in_b([arg.start, arg.end], 3 * sp.pi / 2):
                res_start = -1
            else:
                res_start = np.min([sp.sin(arg.start), sp.sin(arg.end)])
            if self.__check_a_in_b([arg.start, arg.end], sp.pi / 2):
                res_end = 1
            else:
                res_end = np.max([sp.sin(arg.start), sp.sin(arg.end)])
            if res_start == res_end:
                return res_start
            else:
                return Interval(res_start, res_end)
        else:
            return sp.sin(arg)


    def __interval_cos(self, arg):
        """
        Вычисление косинуса для интервала.
        """
        if isinstance(arg, Interval):
            if self.__check_a_in_b([arg.start, arg.end], sp.pi):
                res_start = -1
            else:
                res_start = np.min([sp.cos(arg.start), sp.cos(arg.end)])
            if self.__check_a_in_b([arg.start, arg.end], 2 * sp.pi):
                res_end = 1
            else:
                res_end = np.max([sp.cos(arg.start), sp.cos(arg.end)])
            if res_start == res_end:
                return res_start
            else:
                return Interval(res_start, res_end)
        else:
            return sp.cos(arg)


    def __interval_exp(self, arg):
        """
        Вычисление экспоненты для интервала.
        """
        if isinstance(arg, Interval):
            return Interval(sp.exp(arg.start), sp.exp(arg.end))
        else:
            return sp.exp(arg)

    def __check_a_in_b(self, a: list, b: float) -> bool:
        assert len(a) == 2, "First argument must be an interval of list type."
        a = [a[0] - b, a[1] - b]
        multiple = math.ceil(a[0] / (2 * np.pi)) * (2 * np.pi)
        return multiple <= a[1]