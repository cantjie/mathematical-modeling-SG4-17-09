# encoding=utf-8

import os
COUNT = 0
# 工位数
NUMBER = 50
# 当前时间
time = 0
# 当前充放电电流差
current = 0
# 默认充电电流
IN_CURRENT = 0.5
# 默认放电电流
OUT_CURRENT = 1
# 进入时判别放电还是充电的临界电流
CRITICAL_CURRENT = 0.4
# 记录每个位置是否上机了
LIST = [0 for _ in range(NUMBER)]
# 电池
batteries = []


class Battery:
    """电池类"""
    def __init__(self, index=None, flag=-1, init_current=OUT_CURRENT):
        global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
        self.in_time = time
        self.out_time = -1
        self.flag = flag
        self.power = 0.5  # todo 正态分布,3smg准则
        self.current = init_current
        if index is None:
            LIST[LIST.index(0)] = 1
        else:
            LIST[index] = 1


def run():
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    while True:
        if time % 5 == 0:
            if len(batteries) < NUMBER:
                add_one()
            else:
                # 取出一个电池，放上新的
                get_out_and_add_one()

        for i in range(len(LIST)):
            if LIST[i] == 1:
                if batteries[i].flag == 13 and (batteries[i].power + batteries[i].current * 1/60) > 0.5:
                    # 把这个电池取出来，不一定要放上新的。
                    get_out_one(i)
                    change_current()

        print_status()
        time += 1
        # 时间影响电量
        change_power()


def print_status(name=None):
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    # 每分钟写出一下状态
    if not os.path.isdir('data'):
        os.mkdir('data')
    if name is not None:
        with open('data\\'+str(time)+name+'.txt', 'a', encoding='utf-8') as f:
            for i in range(len(batteries)):
                f.writelines(str(batteries[i].in_time) + '\t' + str(batteries[i].out_time) + '\t' +
                        str(batteries[i].flag) + '\t' + str(batteries[i].power) + '\t' +
                        str(batteries[i].current) + '\t' + str(LIST[i])+'\n')

    else:
        with open('data\\'+str(time)+'.txt', 'a', encoding='utf-8') as f:
            for i in range(len(batteries)):
                f.writelines(str(batteries[i].in_time)+'\t'+str(batteries[i].out_time)+'\t' +
                        str(batteries[i].flag)+'\t'+str(batteries[i].power)+'\t' +
                        str(batteries[i].current)+'\t'+str(LIST[i])+'\n')


def get_out_and_add_one():
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    for i in range(len(LIST)):
        if LIST[i] == 1:
            if batteries[i].flag == 13:
                if batteries[i].power > 0.3:
                    get_out_one(i)
            if batteries[i].flag == 23:
                if batteries[i].power < 0.3:
                    get_out_one(i)
    index = None
    for i in range(len(LIST)):
        if LIST[i] == 0:
            index = i
            break
    if index is None:
        for i in range(len(LIST)):
            if LIST[i] == 1:
                if batteries[i].flag == 13 or batteries[i].flag == 23:
                    if batteries[i].power < 0.5:
                        get_out_one(i)
                        index = i
                        break
    # 输出一下把这东西取出来之后的状态
    print_status('_out_add')
    # 然后这个位置就换成新电池了
    # 但是先要判断一下这个电池进去之后是先放电还是先充电
    if current < CRITICAL_CURRENT:
        batteries[index] = Battery(index, 21)  # 放电
    elif current > IN_CURRENT:
        batteries[index] = Battery(index, 11, IN_CURRENT)  # 充电
    else:
        batteries[index] = Battery(index, 11, current)  # 充电
    change_current()


def add_one():
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    if current < CRITICAL_CURRENT:
        batteries.append(Battery(flag=21))  # 放电
    elif current > IN_CURRENT:
        batteries.append(Battery(flag=11, init_current=IN_CURRENT))  # 充电
    else:
        batteries.append(Battery(flag=11, init_current=current))  # 充电
    change_current()


def get_out_one(index):
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries, COUNT
    # 只是拿出来一个，不放进去
    batteries[index].out_time = time
    batteries[index].flag = -1
    LIST[index] = 0
    change_current()
    COUNT += 1


def change_power():
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    # 每过一分钟，电量就要相应变化
    for i in range(len(LIST)):
        if LIST[i] == 1:
            if batteries[i].flag == 11 or batteries[i].flag == 13 or batteries[i].flag == 22:
                batteries[i].power += batteries[i].current * 1/60
            elif batteries[i].flag == 12 or batteries[i].flag == 21 or batteries[i].flag == 23:
                batteries[i].power -= batteries[i].current * 1/60
            if batteries[i].power >= 1:
                batteries[i].power = 1
                batteries[i].flag += 1
            elif batteries[i].power <= 0:
                batteries[i].power = 0
                batteries[i].flag += 1


def change_current():
    global NUMBER, time, current, IN_CURRENT, OUT_CURRENT, CRITICAL_CURRENT, LIST, batteries
    # 计算并改变当前电流
    out_c = 0
    in_c = 0
    for i in range(len(LIST)):
        if LIST[i] == 1:
            if batteries[i].flag == 11 or batteries[i].flag == 13 or batteries[i].flag == 22:
                in_c += batteries[i].current
            elif batteries[i].flag == 12 or batteries[i].flag == 21 or batteries[i].flag == 23:
                out_c += batteries[i].current
    if out_c - in_c < 0:  # todo 其实应该考虑一下暂停的
        current = 0
    else:
        current = out_c - in_c


if __name__ == "__main__":
    run()
