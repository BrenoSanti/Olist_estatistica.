import unittest

from analise import carregar_dados
from shoe import Shoe, valor_da_mao


class TestShoe(unittest.TestCase):
    def setUp(self):
        self.shoe = Shoe(8)

    def test_composicao_inicial(self):
        self.assertEqual(self.shoe.total_restante, 416)
        self.assertEqual(self.shoe.restantes["A"], 32)
        self.assertEqual(self.shoe.restantes["10"], 128)
        self.assertAlmostEqual(sum(self.shoe.probabilidades_proxima_carta().values()), 1.0)

    def test_remocao_e_reset(self):
        self.shoe.registrar_observadas(["A", "K", "10"])
        self.assertEqual(self.shoe.total_restante, 413)
        self.assertEqual(self.shoe.restantes["A"], 31)
        self.assertEqual(self.shoe.restantes["10"], 126)
        self.shoe.reiniciar()
        self.assertEqual(self.shoe.total_restante, 416)

    def test_remocao_atomica_invalida(self):
        with self.assertRaises(ValueError):
            self.shoe.registrar_observadas(["A"] * 33)
        self.assertEqual(self.shoe.total_restante, 416)

    def test_valores_com_as(self):
        self.assertEqual(valor_da_mao(["10", "6"]), 16)
        self.assertEqual(valor_da_mao(["A", "6"]), 17)
        self.assertEqual(valor_da_mao(["A", "6", "10"]), 17)

    def test_bust_mao_16_shoe_novo(self):
        # 6, 7, 8, 9 e cartas de valor 10 causam bust: 256/416.
        self.assertAlmostEqual(self.shoe.probabilidade_bust(["10", "6"]), 256 / 416)


class TestDados(unittest.TestCase):
    def test_csv_tem_100_mil_linhas(self):
        self.assertEqual(len(carregar_dados()), 100_000)


if __name__ == "__main__":
    unittest.main()
