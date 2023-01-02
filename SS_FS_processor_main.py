import os
import argparse

# Author S.W

MemSize = 1000  # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.


class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        with open(ioDir + "/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]
        # initialInstructions = self.readInstr(self.IMem)
        # print("Initial instructions is : ",initialInstructions);

    def readInstr(self):
        with open(ioDir + "/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]
        # read instruction memory
        # return 32 bit hex val
        lenInstruction = int(len(self.IMem) / 4)
        initialInstructions = [0] * lenInstruction
        # we store the initial insructions in this array initialInstructions, every index represents one instruction
        for i in range(lenInstruction):
            initialInstructions[i] = self.IMem[4 * i] + self.IMem[4 * i + 1] + self.IMem[4 * i + 2] + self.IMem[
                4 * i + 3];
            # print(initialInstructions[i]);
        return initialInstructions
        pass


class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "/dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
        for i in range(len(self.DMem), 1000):
            self.DMem.append("00000000")

    def readInstr(self):
        # read data memory
        # return 32 bit hex val
        lenDataMemory = int(len(self.DMem) / 4)
        initialDataMemory = [0] * lenDataMemory
        # we store the initial data memory in this array initialDataMemory, every index represents one instruction
        for i in range(lenDataMemory):
            initialDataMemory[i] = self.DMem[4 * i] + self.DMem[4 * i + 1] + self.DMem[4 * i + 2] + self.DMem[
                4 * i + 3];
            # print(initialDataMemory[i]);
        return initialDataMemory
        pass

    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory
        pass

    def outputDataMem(self):
        resPath = self.ioDir + "/" + self.id + "_DMEMResult.txt"
        # print(len(self.DMem));
        for i in range(len(self.DMem), 1000):
            self.DMem.append("00000000")
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])


class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]

    def readRF(self, Reg_addr):
        # Fill in

        s = self.Registers[int(Reg_addr, 2)]
        # print("self.Registers):",s)
        if s == 0: return s
        # s = s[1:]
        if s[0] == '1':
            s = s.replace('1', '2')
            s = s.replace('0', '1')
            s = s.replace('2', '0')
            s = -1 * (int(s, 2) + 1)
        else:
            s = (int(s, 2))
        # print(s)
        return s

    def writeRF(self, enable, Reg_addr, Wrt_reg_data):
        # Fill in
        if enable == 0: pass
        if Reg_addr != 0:
            if Wrt_reg_data >= 0:
                # print("-------",bin(Wrt_reg_data))
                Wrt_reg_data = bin(Wrt_reg_data)[2:].zfill(32)
                # print(Wrt_reg_data)
            else:
                s = bin(-Wrt_reg_data)[3:].zfill(32);
                s = s.replace('1', '2')
                s = s.replace('0', '1')
                s = s.replace('2', '0')
                Wrt_reg_data = bin(int(s, 2) + 1)[2:]

            self.Registers[Reg_addr] = Wrt_reg_data


    def outputRF(self, cycle):
        op = ["State of RF after executing cycle: " + str(cycle) + "\n"]
        # print("output",self.outputFile)
        for val in self.Registers:
            if val == 0:
                val = int(val)
                val = bin(val)[2:]
            val = val.zfill(32)

            op.extend([str(val) + "\n"])
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class State(object):
    def __init__(self):
        self.IF = {"PC": 0, "nop": 0}
        self.ID = {"Instr": 0, "nop": 1}
        self.EX = {"Operand1": 0, "Operand2": 0, "StData": 0, "DestReg": 0, "alu_op": 0, "UpdatePC": 0,
                   "wrt_enable": 0, "rd_mem": 0, "wrt_mem": 0, "stallOver": 0, "nop": 1, "is_I_type": 0, "Imm": 0, "func7":0}
        self.MEM = {"ALUresult": 0, "Store_data": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                    "wrt_mem": 0, "wrt_enable": 0, "nop": 1, "stallOver": 0}
        self.WB = {"Wrt_data": 0, "Wrt_reg_addr": 0, "wrt_enable": 0, "nop": 1}


class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem


def sign_ext(imm):
    if imm[0] == '1':
        s = imm[1:]
        s = s.replace('1', '2')
        s = s.replace('0', '1')
        s = s.replace('2', '0')
        s = int(s, 2) + 1
        s = -s
    else:
        s = int(imm, 2)
    return s


class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"
        self.opFilePath2 = ioDir + "/PerformanceMetrics.txt"
        # print("ssssss",self.opFilePath)

    def decoder(self, instruction):
        oc, rd, rs1, rs2, reg_wr_en = [], [], [], [], []
        for i in range(0, len(instruction)):
            oc.append(instruction[i][25:32])
            rd.append(instruction[i][20:25])
            rs1.append(instruction[i][12:17])
            rs2.append(instruction[i][7:12])
            if oc[i] == "0110011":
                reg_wr_en.append(1);
            else:
                reg_wr_en.append(0);

        # rs1, rs2, rd, oc, reg_wr_en
        # print(reg_wr_en)
        return rs1, rs2, rd, oc, reg_wr_en

    def alu(self, op1, op2, instru):
        result = 0;
        func7 = instru[0:7]
        func3 = instru[17:20]
        if instru[25:32] == "0110011":
            if func3 == "000" and func7 == "0000000":
                # add

                result = op1 + op2
            elif func3 == "000" and func7 == "0100000":
                # print("This sub")
                result = op1 - op2
                # return result;
            elif func3 == "100":
                # xor
                result = op1 ^ op2
            elif func3 == "110":
                # or
                result = op1 | op2
            elif func3 == "111":
                # and
                result = op1 & op2

        elif instru[25:32] == "0010011":
            # this is I
            imm = op2
            if func3 == "000":  # addi
                result = imm + op1
            elif func3 == "100":  # xori
                result = imm ^ op1
            elif func3 == "110":  # ori
                result = imm | op1
            elif func3 == "111":  # andi
                result = imm & op1

        elif instru[25:32] == "1111111":
            # print("This is halt")
            self.state.IF["nop"] = 1;
        return result

    def step(self):
        self.myRF.writeRF(self.state.WB['wrt_enable'], self.state.WB['Wrt_reg_addr'], self.state.WB['Wrt_data'])
        # Your implementation
        instruction = self.ext_imem.readInstr();
        dataMemory = self.ext_dmem.readInstr();
        rs1, rs2, rd, oc, reg_wr_en = self.decoder(instruction)
        result = 0
        i = 0
        while i < len(oc):
            self.state.WB['wrt_enable'] = 1;

            if (i <= len(oc) - 1):
                if int(rd[i], 2) == 0:
                    self.state.WB['wrt_enable'] = 0
                if oc[i] == "0000011":
                    # print("lw")
                    imm = instruction[i][0:10]
                    imm = sign_ext(imm) + int(rs1[i], 2)
                    self.myRF.writeRF(self.state.WB['wrt_enable'], int(rd[i], 2), (int(dataMemory[imm], 2)))


                elif oc[i] == "0010011":
                    # print("I type")
                    imm = instruction[i][0:12]
                    op1 = self.myRF.readRF(rs1[i])
                    op2 = sign_ext(imm);
                    self.state.EX['Read_data1'] = op1
                    self.state.EX['Read_data2'] = op2
                    result = self.alu(self.state.EX['Read_data1'], self.state.EX['Read_data2'], instruction[i])

                    self.myRF.writeRF(self.state.WB['wrt_enable'], int(rd[i], 2), result)

                elif oc[i] == "1101111":
                    # this is JAL
                    imm = sign_ext(
                        instruction[i][0] + instruction[i][12:20] + instruction[i][11] + instruction[i][1:11]) * 2
                    self.myRF.writeRF(self.state.WB['wrt_enable'], int(rd[i], 2), self.state.IF['PC'] + 4)
                    self.state.IF['PC'] = (self.state.IF['PC'] + imm) - 4
                    # print(self.state.IF['PC'])
                    i = int((self.state.IF['PC']) / 4)

                elif oc[i] == "1100011":
                    # print("this is B")
                    op1 = self.myRF.readRF(rs1[i])
                    op2 = self.myRF.readRF(rs2[i])
                    imm = sign_ext(
                        instruction[i][0] + instruction[i][24] + instruction[i][1:7] + instruction[i][20:24]) * 2
                    func3 = instruction[i][17:20]
                    # print(imm)

                    if func3 == "000":
                        # BEQ
                        # print("beq")
                        # PC = (rs1 == rs2)?PC + sign_ext(imm): PC + 4
                        if op1 == op2:
                            self.state.IF['PC'] = (self.state.IF['PC'] + imm) - 4
                            i = int((self.state.IF['PC']) / 4)

                    elif func3 == "001":
                        # BNE
                        if op1 != op2:
                            self.state.IF['PC'] = (self.state.IF['PC'] + imm) - 4
                            i = int((self.state.IF['PC']) / 4)

                elif oc[i] == "0110011":
                    # print("R type")
                    op1 = self.myRF.readRF(rs1[i])
                    op2 = self.myRF.readRF(rs2[i])
                    self.state.EX['Read_data1'] = op1
                    self.state.EX['Read_data2'] = op2

                    result = self.alu(self.state.EX['Read_data1'], self.state.EX['Read_data2'], instruction[i])
                    self.myRF.writeRF(self.state.WB['wrt_enable'], int(rd[i], 2), result)

                elif oc[i] == "0100011":
                    # print("S type")
                    # data[rs1 + sign_ext(imm)][31:0] = rs2
                    imm = instruction[i][0:7]+instruction[i][20:25]
                    imm = (sign_ext(imm) + int(rs1[i], 2)) - 1
                    # print(imm)
                    for u in range(1, 5):
                        if self.myRF.readRF(rs2[i]) == 0:
                            self.ext_dmem.DMem[imm+u] = (
                                bin(self.myRF.Registers[int(rs2[i], 2)])[2:].zfill(32)[(u - 1) * 8:u * 8])
                        else:
                            self.ext_dmem.DMem[imm+ u] = (
                                self.myRF.Registers[int(rs2[i], 2)][(u - 1) * 8:u * 8])
                    dataMemory.append(result)

                elif oc[i] == "1111111":
                    # print("halt type", "------------")
                    self.state.IF["nop"] = 1
                    self.myRF.outputRF(self.cycle)  # dump RF
                    self.printState(self.nextState,
                                    self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...
                    self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
                    self.cycle += 1
                    self.myRF.outputRF(self.cycle)  # dump RF
                    self.printState(self.nextState,
                                    self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...
                    self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
                    self.cycle += 1
                    break
                self.nextState.IF['PC'] += 4
            i += 1
            if self.state.IF["nop"]:
                self.halted = True

            self.nextState.WB['Wrt_data'] = result
            self.nextState.WB['Wrt_reg_addr'] = rd
            self.nextState.WB['wrt_enable'] = reg_wr_en
            self.halted = True
            self.myRF.outputRF(self.cycle)  # dump RF
            self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...
            self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
            self.cycle += 1

        totalExecutionCycleSS = self.cycle
        instructionsPerCycleSS = len(instruction) / totalExecutionCycleSS
        averageCPISS = 1 / instructionsPerCycleSS

        # print("Average CPI is", averageCPISS)
        # print("Instructions per cycle is", instructionsPerCycleSS)
        # print("Total execution cycles is", totalExecutionCycleSS)

        with open(self.opFilePath2, "w") as wf:
            print(self.ioDir)
            printstate = ["Single Stage Core Performance Metrics-----------------------------" + "\n"]
            printstate.append("Number of cycles taken: " + str(totalExecutionCycleSS) + "\n")
            printstate.append("Cycles per instruction: " + str(averageCPISS) + "\n")
            printstate.append("Instructions per cycle: " + str(instructionsPerCycleSS) + "\n")
            printstate.append("\n")
            wf.writelines(printstate)

    def printState(self, state, cycle):
        printstate = ["State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


class FiveStageCore(Core):
    def sign_ext(self, imm):
        if imm[0] == '1':
            s = imm[1:]
            s = s.replace('1', '2')
            s = s.replace('0', '1')
            s = s.replace('2', '0')
            s = int(s, 2) + 1
            s = -s
        else:
            s = int(imm, 2)
        return s

    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"
        self.opFilePath2 = ioDir + "/PerformanceMetrics.txt"

    def decoder(self, instruction):
        oc, rd, rs1, rs2, reg_wr_en = 0, 0, 0, 0, 0
        for i in range(0, len(instruction)):
            oc = (instruction[25:32])
            rd = (instruction[20:25])
            rs1 = (instruction[12:17])
            rs2 = (instruction[7:12])
            if oc == "0110011":
                reg_wr_en = 1
            else:
                reg_wr_en = 0

        return rs1, rs2, rd, oc, reg_wr_en


    def inttobinary(self, int):
        if int >= 0:
            int = bin(int)[2:].zfill(32)
        else:
            s = bin(-int)[3:].zfill(32);
            s = s.replace('1', '2')
            s = s.replace('0', '1')
            s = s.replace('2', '0')
            int = bin(int(s, 2) + 1)[2:]
        return int
    def step(self):
        # Your implementation
        instructions = self.ext_imem.readInstr()
        dataMemory = self.ext_dmem.readInstr();
        # print(dataMemory)
        print("This is 5 stage---------------------------")

        # while self.state.IF["PC"] / 4 < len(instructions):
        while (self.state.IF["nop"]==0 or self.state.ID["nop"]==0 or self.state.EX["nop"]==0 or self.state.MEM["nop"]==0 or self.state.WB["nop"]==0):
            self.state.EX['StData'] = str(self.state.EX['StData']).zfill(32)
            self.state.EX['Operand1'] = str(self.state.EX['Operand1']).zfill(32)
            self.state.EX['Operand2'] = str(self.state.EX['Operand2']).zfill(32)
            self.state.EX['DestReg'] = str(self.state.EX['DestReg']).zfill(5)
            self.state.EX['alu_op'] = str(self.state.EX['alu_op']).zfill(2)
            self.state.MEM['ALUresult'] = str(self.state.MEM['ALUresult']).zfill(32)
            self.state.MEM['Store_data'] = str(self.state.MEM['Store_data']).zfill(32)
            self.state.MEM['Wrt_reg_addr'] = str(self.state.MEM['Wrt_reg_addr']).zfill(5)
            self.state.WB['Wrt_data'] = str(self.state.WB['Wrt_data']).zfill(32)
            self.state.WB['Wrt_reg_addr'] = str(self.state.WB['Wrt_reg_addr']).zfill(5)


            # --------------------- WB stage ---------------------

            if 0 == self.state.WB['nop']:
                if 1 == self.state.WB['wrt_enable']:
                    self.myRF.writeRF(1, int(self.state.WB['Wrt_reg_addr'], 2),
                                      int(dataMemory[self.state.EX['wrt_mem']], 2))
                if self.state.IF['PC']==len(instructions)*4-4:
                    self.state.IF['nop'] = 1

            # # --------------------- MEM stage --------------------
            if 0 == self.state.MEM['nop']:

                if 0== self.state.MEM['rd_mem']:
                    self.nextState.WB['Wrt_data'] = self.state.MEM['ALUresult']
                # "MEM-MEM sw Forwarding"
                elif 1 == self.state.MEM['wrt_mem']:
                    # need to store to memory
                    if (0 == self.state.WB['nop']) and (1 == self.state.WB['wrt_enable']) and (
                            self.state.WB['Wrt_reg_addr'] == self.state.MEM['Wrt_reg_addr']):
                        self.state.MEM['Store_data'] = self.state.WB['Wrt_data']
                    self.myRF.writeRF(1, int(self.state.MEM['ALUresult'],2), int(self.state.MEM['Store_data'],2))
                    self.nextState.WB['Wrt_data'] = self.state.MEM['Store_data']
                #
                elif self.state.MEM['wrt_enable'] and int(self.state.MEM['ALUresult'],2)!=0:
                    # print(self.state.MEM['ALUresult'],self.cycle,self.nextState.WB['Wrt_reg_addr'])
                    self.myRF.writeRF(1, int(self.nextState.WB['Wrt_reg_addr'],2),int(self.state.MEM['ALUresult'], 2))

                    # self.myRF.writeRF(self.nextState.WB['wrt_enable'], int(rd[i], 2), result)
                    self.nextState.WB['Wrt_data'] = self.state.MEM['ALUresult']
                    add=int(self.nextState.WB['Wrt_reg_addr'],2)+4
                    for u in range(1, 5):
                        # print(add)
                        self.ext_dmem.DMem[add+u] = self.state.MEM['ALUresult'][(u - 1) * 8:u * 8]

            self.nextState.WB['nop'] = self.state.MEM['nop']
            self.nextState.WB['Wrt_reg_addr'] = self.state.MEM['Wrt_reg_addr']
            self.nextState.WB['wrt_enable'] = self.state.MEM['wrt_enable']

            # dataMemoryindex=int(self.state.MEM['Wrt_reg_addr'], 2)
            # if (dataMemoryindex!=0):
            #     self.nextState.WB['Wrt_data'] = dataMemory[dataMemoryindex-1]

            # --------------------- EX stage ---------------------


            self.nextState.MEM['nop'] = self.state.EX['nop']
            num1 = int(self.state.EX['Operand1'], 2)
            num2 = int(self.state.EX['Operand2'], 2)

            if (self.state.EX['alu_op'] == "00"):
                if (self.state.EX['Imm'] == 0):
                    self.nextState.MEM['ALUresult'] = self.inttobinary(num1 + num2)
                else:
                    self.nextState.MEM['ALUresult'] = self.inttobinary(num1 - num2)
            elif (self.state.EX['alu_op'] == "01"):
                self.nextState.MEM['ALUresult'] = self.inttobinary(num1 ^ num2)
            elif (self.state.EX['alu_op'] == "10"):
                self.nextState.MEM['ALUresult'] = self.inttobinary(num1 | num2)
            elif (self.state.EX['alu_op'] == "11"):
                self.nextState.MEM['ALUresult'] = self.inttobinary(num1 & num2)

            self.nextState.MEM['rd_mem'] = self.state.EX['rd_mem']
            self.nextState.MEM['wrt_mem'] = self.state.EX['wrt_mem']
            self.nextState.MEM['wrt_enable'] = self.state.EX['wrt_enable']
            self.nextState.MEM['Wrt_reg_addr'] = self.state.EX['DestReg']
            self.nextState.MEM['nop'] = self.state.EX['nop'];
            if (0 == self.state.EX['nop']):

                # wb forwarding to rs1
                if ((0 == self.state.WB['nop']) and (1 == self.state.WB['wrt_enable']) and (
                        self.state.WB['Wrt_data'] == self.state.EX['Operand1'])):
                    self.state.EX['Operand1'] = self.state.WB['Wrt_data']

                # wb forwarding to rs2
                if ((0 == self.state.WB['nop']) and (1 == self.state.WB['wrt_enable']) and (
                        self.state.WB['Wrt_data'] == self.state.EX['Operand2'])):
                    if (((0 == self.state.EX['is_I_type']) and (1 == self.state.EX['wrt_enable'])) or (
                            1 == self.state.EX['wrt_mem'])):
                        self.state.EX['Operand2'] = self.state.WB['Wrt_data']

                # mem to ex
                if ((0 == self.state.MEM['nop']) and (0 == self.state.MEM['rd_mem']) and (
                        0 == self.state.MEM['wrt_mem']) and (
                        1 == self.state.MEM['wrt_enable']) and (self.state.MEM['Store_data'] == self.state.EX['Operand1'])):
                    self.state.EX['Operand1'] = self.state.MEM['ALUresult']

                # mem to ex
                if ((0 == self.state.MEM['nop']) and (0 == self.state.MEM['rd_mem']) and (
                        0 == self.state.MEM['wrt_mem']) and (
                        1 == self.state.MEM['wrt_enable']) and (self.state.MEM['Store_data'] == self.state.EX['Operand2'])):
                    if ((0 == self.state.EX['is_I_type']) and (1 == self.state.EX['wrt_enable'])):
                        self.state.EX['Operand2'] = self.state.MEM['ALUresult']

                #
                if (0 == self.state.EX['is_I_type']):
                    if (1 == self.state.EX['wrt_enable']):
                        num1 = int(self.state.EX['Operand1'],2)
                        num2 = int(self.state.EX['Operand2'],2)
                        if (self.state.EX['alu_op'] == '00'):
                            if (self.state.EX['Imm']==0):
                                self.nextState.MEM['ALUresult'] = self.inttobinary(num1 + num2)
                            else:
                                self.nextState.MEM['ALUresult'] = self.inttobinary(num1 - num2)
                        elif (self.state.EX['alu_op'] == '01'):
                            self.nextState.MEM['ALUresult'] = self.inttobinary(num1 ^ num2)
                        elif (self.state.EX['alu_op'] == '10'):
                            self.nextState.MEM['ALUresult'] = self.inttobinary(num1 | num2)
                        elif (self.state.EX['alu_op'] == '11'):
                            self.nextState.MEM['ALUresult'] = self.inttobinary(num1 & num2)
                    else:
                        self.nextState.MEM['ALUresult'] = 0;


                elif (1 == self.state.EX['is_I_type']):
                    if (self.state.EX['alu_op'] == 0):
                        if (self.state.EX['func7'] == "0000000"):
                            self.nextState.MEM['ALUresult'] = self.state.EX['Operand1'] + self.sign_ext(self.state.EX['Imm'])
                        else:
                            self.nextState.MEM['ALUresult'] = self.state.EX['Operand1'] - self.sign_ext(self.state.EX['Imm'])
                    elif (self.state.EX['alu_op'] == 1):
                        self.nextState.MEM['ALUresult'] = self.state.EX['Operand1'] ^ self.sign_ext(self.state.EX['Imm'])
                    elif (self.state.EX['alu_op'] == 2):
                        self.nextState.MEM['ALUresult'] = self.state.EX['Operand1'] | self.sign_ext(self.state.EX['Imm'])
                    elif (self.state.EX['alu_op'] == 3):
                        self.nextState.MEM['ALUresult'] = self.state.EX['Operand1'] & self.sign_ext(self.state.EX['Imm'])


                self.nextState.MEM['Store_data'] = self.state.EX['StData'];
                self.nextState.MEM['Wrt_reg_addr'] = self.state.EX['DestReg'];
                self.nextState.MEM['wrt_enable'] = self.state.EX['wrt_enable'];
                self.nextState.MEM['rd_mem'] = self.state.EX['rd_mem'];
                self.nextState.MEM['wrt_mem'] = self.state.EX['wrt_mem'];

            self.nextState.MEM['wrt_mem'] = self.state.EX['wrt_mem'];
            self.nextState.MEM['wrt_enable'] = self.state.EX['wrt_enable']
            self.nextState.MEM['Wrt_reg_addr'] = self.state.EX['DestReg']
            self.nextState.MEM['rd_mem'] = self.state.EX['rd_mem'];


            # # --------------------- ID stage ---------------------
            if (0 == self.state.ID['nop']):
                Instr = self.state.ID['Instr']
                opcode = Instr[25:32]
                func7 = Instr[0:7]
                func3 = Instr[17:20]
                rd = Instr[20:25]

                rs1 = Instr[12:17]  # rt is rs1
                rs2 = Instr[7:12]  # rs is rs2

                if (opcode == "0000011"):
                    print("lw")
                    imm = Instr[0:10]
                    imm = sign_ext(imm) + int(rs1, 2)
                    self.nextState.EX['DestReg'] = rd
                    self.nextState.EX['is_I_type'] = 1
                    self.nextState.EX['alu_op'] = '00'
                    self.nextState.EX['wrt_enable'] = 1
                    self.nextState.EX['rd_mem'] = 1
                    self.nextState.EX['wrt_mem'] = imm
                    self.nextState.EX['nop'] = 0

                    # // Load Word R[rd] = M[R[rs]
                    # rd = mem[rs1 + signa(imm)][31:0]

                elif (opcode == "0100011"):
                    print("sw")
                    imm = Instr[0:7] + Instr[20:25]
                    imm = (sign_ext(imm) + int(rs1, 2)) - 1
                    # print(rs2,"rs2----")

                    self.nextState.EX['DestReg'] = rs2
                    self.nextState.EX['is_I_type'] = 0
                    self.nextState.EX['alu_op'] = '00'
                    self.nextState.EX['wrt_enable'] = 0
                    self.nextState.EX['rd_mem'] = 0
                    self.nextState.EX['wrt_mem'] = 1

                elif (opcode == "0110011"):
                    # R type
                    print("R type")
                    # print(rs1,rs2)
                    self.nextState.EX['DestReg'] = rd
                    self.nextState.EX['is_I_type'] = 0
                    if (func7 == "0000000"):
                        self.nextState.EX['func7'] = func7
                        if (func3 == "000"):
                            # add
                            self.nextState.EX['alu_op'] = '00'
                        elif (func3 == "100"):
                            self.nextState.EX['alu_op'] = '01'
                        elif (func3 == "110"):
                            self.nextState.EX['alu_op'] = '10'
                        elif (func3 == "111"):
                            self.nextState.EX['alu_op'] = '11'

                    elif (func7 == "0100000"):
                        # sub
                        self.nextState.EX['alu_op'] = '00'

                    self.nextState.EX['wrt_enable'] = 1;
                    self.nextState.EX['rd_mem'] = 1
                    self.nextState.EX['wrt_mem'] = 0;

                    if (self.nextState.EX['nop'] == 0):
                        # print(" jinru ex", self.cycle, self.myRF.Registers)
                        self.nextState.EX['Operand1'] = dataMemory[int(rs1, 2) - 1]
                        self.nextState.EX['Operand2'] = dataMemory[int(rs2, 2) - 1]
                        # self.nextState.EX['DestReg'] = self.myRF.Registers[int(rd, 2)]

                elif (opcode == "0110011"):
                    # I type
                    self.nextState.EX['DestReg'] = rd
                    self.nextState.EX['is_I_type'] = 1

                    imm = Instr[0:12]
                    op1 = self.myRF.readRF(rs1)
                    op2 = sign_ext(imm)

                    if (func3 == "000"):
                        # addi
                        self.nextState.EX['alu_op'] = '00'
                    elif (func3 == "100"):
                        self.nextState.EX['alu_op'] = '01'
                    elif (func3 == "110"):
                        self.nextState.EX['alu_op'] = '10'
                    elif (func3 == "111"):
                        self.nextState.EX['alu_op'] = '11'

                    self.nextState.EX['wrt_enable'] = 1;
                    self.nextState.EX['rd_mem'] = 0;
                    self.nextState.EX['wrt_mem'] = 0;

                if (0 == self.state.EX['nop']) and (1 == self.state.EX['rd_mem']) and (
                        self.state.EX['DestReg'] == rd) and (
                        (self.state.EX['DestReg'] != 0) and (0 == self.nextState.EX['is_I_type'])):
                    print("------stall------")
                    #  stall

                    self.state.ID['nop'] = 0
                    self.nextState.EX['nop'] = 1;
                    self.nextState.EX['DestReg'] = self.state.EX['DestReg'];
                    self.nextState.ID = self.state.ID;
                    self.nextState.IF = self.state.IF;

                    self.printState(self.nextState, self.cycle);
                    self.myRF.outputRF(self.cycle)
                    self.state = self.nextState;

                    self.nextState.EX['Halt'] = 1
                    self.nextState.EX['rd_mem'] = 0
                    self.cycle += 1
                    continue

            self.nextState.EX['nop'] = self.state.ID['nop'];
            # --------------------- IF stage ---------------------
            if (self.state.IF["PC"] / 4 < len(instructions)):
                # print("cycle")
                if 0 == self.state.IF['nop']:
                    instruction = instructions[int(self.state.IF["PC"] / 4)]
                    # print(instruction)
                    if instruction != 0xffffffff:
                        self.nextState.IF["PC"] = self.state.IF["PC"] + 4
                        self.nextState.IF['nop'] = 0;
                    else:
                        self.state.IF['nop'] = 1;
                        self.nextState.IF["PC"] = self.state.IF["PC"];
                        self.nextState.IF['nop'] = 1;

                    self.nextState.ID['Instr'] = instruction
            self.nextState.ID['nop'] = self.state.IF['nop']
            if (self.cycle > 1000): break; #avoid the error
            self.halted = True
            if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and \
                    self.state.WB["nop"]:
                self.halted = True
                break

            self.myRF.outputRF(self.cycle)  # dump RF
            self.printState(self.nextState, self.cycle)  # print states after executing cycle 0, cycle 1, cycle 2 ...

            self.state = self.nextState  # The end of the cycle and updates the current state with the values calculated in this cycle
            self.cycle += 1

        """
                print("Average CPI is", averageCPIFF)
                print("Instructions per cycle is", instructionsPerCycleFF)
                print("Total execution cycles is", totalExecutionCycleFF)
        """
        self.cycle += 1
        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(self.nextState, self.cycle)
        totalExecutionCycleSS = self.cycle+1
        instructionsPerCycleSS = len(instructions) / totalExecutionCycleSS
        averageCPISS = 1 / instructionsPerCycleSS

        with open(self.opFilePath2, "a") as wf:
            # print(self.ioDir)
            printstate = ["Five Stage Core Performance Metrics-----------------------------" + "\n"]
            printstate.append("Number of cycles taken: " + str(totalExecutionCycleSS) + "\n")
            printstate.append("Cycles per instruction: " + str(averageCPISS) + "\n")
            printstate.append("Instructions per cycle: " + str(instructionsPerCycleSS) + "\n")
            printstate.append("\n")
            wf.writelines(printstate)

    def printState(self, state, cycle):
        printstate = ["-" * 70 + "\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend("\n")
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend("\n")
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend("\n")
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in self.state.EX.items()])
        printstate.extend("\n")
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in self.state.MEM.items()])
        printstate.extend("\n")
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in self.state.WB.items()])

        if (cycle == 0):
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)
        with open(self.opFilePath2, "a") as wf:
            printstate = []
            wf.writelines(printstate)


if __name__ == "__main__":

    # parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    # print("IO Directory:", ioDir)
    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

    print("This is single stage----------------------")
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while (True):
        if not ssCore.halted:
            ssCore.step()

        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break

    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()
