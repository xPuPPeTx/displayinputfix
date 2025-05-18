#chainy, tg: zxchainzxc

import winreg

print("chainy, tg: zxchainzxc\n")

# Ввод исходного ключа без \00 в конце
source_input = input("Введите полный путь к основному монитору с которого копировать данные (без \\00): ")
source_key_path_00 = source_input.split("HKEY_LOCAL_MACHINE\\")[1].strip() + "\\00"
source_key_path_0000 = source_key_path_00 + "\\00"

res = input('Введите исходное разрешение монитора через x (например, 1920x1080): ').split('x')[0]
stride = ((int(res) * 32 + 7) // 8)
print("Stride:", stride)

print('\nБудут скопированы данные из путей:')
print(source_key_path_00)
print(source_key_path_0000)

def list_subkeys():
    subkeys = []
    base_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Configuration"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(key, i)
                    # Формируем полный путь к подпапке с \00
                    full_path = base_path + "\\" + name + "\\00"
                    if full_path.lower() != source_key_path_00.lower():
                        subkeys.append(full_path)
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"Ошибка при чтении ключей: {e}")
    return subkeys

target_key_paths_00 = list_subkeys()
target_key_paths_0000 = [path + "\\00" for path in target_key_paths_00]


def copy_values(source_key, target_key):
    try:
        i = 0
        while True:
            value = winreg.EnumValue(source_key, i)
            name, val, valtype = value
            winreg.SetValueEx(target_key, name, 0, valtype, val)
            i += 1
    except OSError:
        pass  # Конец списка значений

def set_stride(root, path):
    try:
        # Открываем ключ на запись (создаёт, если не существует)
        key = winreg.CreateKey(root, path)
        winreg.SetValueEx(key, "Stride", 0, winreg.REG_DWORD, stride)
        key.Close()
        print(f"Параметр Stride создан в {path}")
    except Exception as e:
        print(f"Ошибка при создании Stride в {path}: {e}")

def main():
    root = winreg.HKEY_LOCAL_MACHINE

    # Создаём/обновляем Stride в исходных ключах (source)
    set_stride(root, source_key_path_00)
    set_stride(root, source_key_path_0000)

    with winreg.OpenKey(root, source_key_path_00, 0, winreg.KEY_READ) as src_key_00, \
         winreg.OpenKey(root, source_key_path_0000, 0, winreg.KEY_READ) as src_key_0000:

        # Копируем значения из \00 в целевые \00
        for target_path_00 in target_key_paths_00:
            try:
                tgt_key_00 = winreg.CreateKey(root, target_path_00)
                copy_values(src_key_00, tgt_key_00)
                # Создаём Stride у целевого ключа
                winreg.SetValueEx(tgt_key_00, "Stride", 0, winreg.REG_DWORD, stride)
                tgt_key_00.Close()
                print(f"Скопированы значения и создан Stride в {target_path_00}")
            except Exception as e:
                print(f"Ошибка при копировании в {target_path_00}: {e}")

        # Копируем значения из \00\00 в целевые \00\00
        for target_path_0000 in target_key_paths_0000:
            try:
                tgt_key_0000 = winreg.CreateKey(root, target_path_0000)
                copy_values(src_key_0000, tgt_key_0000)
                # Создаём Stride у целевого ключа
                winreg.SetValueEx(tgt_key_0000, "Stride", 0, winreg.REG_DWORD, stride)
                tgt_key_0000.Close()
                print(f"Скопированы значения и создан Stride в {target_path_0000}")
            except Exception as e:
                print(f"Ошибка при копировании в {target_path_0000}: {e}")

    input('Готово, осталось удалить монитор из диспетчера устройств, перезагрузить ПК и сам монитор. Нажмите Enter для выхода.\n')

if __name__ == "__main__":
    main()
