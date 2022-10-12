from random import randint

# Сортирует Itarable по неубыванию z_index. Объекты с z_index=0 помещаются на случанйые позиции
def shuffle_by_z_index(seq) -> None:
    for i, s in enumerate(seq):
        if not s.z_index:
            j = randint(0, len(seq) - 1)
            seq[i], seq[j] = seq[j], seq[i]