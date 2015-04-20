# -*- coding: utf8 -*-
__author__ = '54'
from vboxapi.VirtualBox_constants import VirtualBoxReflectionInfo
import shutil
import os
import re
from os.path import join, getsize

from win32com import client
import pythoncom
import psutil
import wmi


class VboxControl():
    def __init__(self,parent=None):
        pythoncom.CoInitialize()#win32com初始化什么的东西
        #-----------------vboxapi相关控制对象初始化-------------------
        self.vboxCnst=VirtualBoxReflectionInfo(0)
        self.vboxCnstNum=VirtualBoxReflectionInfo(1)
        self.vbox=client.Dispatch("VirtualBox.VirtualBox")
        self.session=client.Dispatch("VirtualBox.Session")#普通操作使用的公用session
        self.SessionDict={}#使用一个字典储存所有运行的虚拟机对应的session对象,便于操作.但只能储存于内存中
        self.host=self.vbox.Host
        #vm1=vbox.FindMachine("Test1")
        #vm_xp=vbox.FindMachine("xp")
        self.syspro=self.vbox.SystemProperties
        self.PerformanceCache={}#虚拟机性能字典,虚拟机名称为键,性能数据为值
        self.VboxInstallPath=os.getenv('VBOX_MSI_INSTALL_PATH')
        self.FtpPath=(os.getenv('VBOX_MSI_INSTALL_PATH'))[:2]+'\\Ftp_Folder'
        self.wmi_obj=wmi.WMI()
        #self.vm_list=[]
        #vbox_init()
        #-----------------vboxapi相关控制对象初始化结束-------------------
    State_dict={
        18:'DeletingSnapshotPaused',
        15:'TeleportingIn',
         7:'Stuck',
        16:'FaultTolerantSyncing',
        13:'Restoring',
        14:'TeleportingPausedVM',
         5:'Running',
         4:'Aborted',
         1:'PoweredOff',
         3:'Teleported',
        11:'Stopping',
        18:'LastOnline',
        10:'Starting',
        12:'Saving',
         8:'FirstTransient',
         9:'LiveSnapshotting',
         5:'FirstOnline',
         6:'Paused',
         21:'LastTransient',
         20:'DeletingSnapshot',
          0:'Null',
          2:'Saved',
         19:'RestoringSnapshot',
         17:'DeletingSnapshotOnline'
    }

        #设备类型字典
    DeviceType_dict={
                0:'Null',
                1:'Floppy',
                2:'DVD',
                3:'HardDisk',
                4:'Network',
                5:'USB',
                6:'SharedFolder'
            }

        #剪贴板设定类型字典
    ClipboardMode_dict={
            1:'HostToGuest',
             2:'GuestToHost',
             3:'Bidirectional'
        }

        #Session状态类型字典
    SessionState_dict={
            1:'Unlocked',
            3:'Spawning',
            4:'Unlocking',
            2:'Locked'
        }

        #StorageBus状态类型字典
    StorageBus_dict={
            4:'Floppy',
            2:'SATA',
            5:'SAS',
            3:'SCSI',
            1:'IDE'
        }

        #StorageControllerType状态类型字典
    StorageControllerType_dict={
            5:'PIIX4',
            3:'IntelAhci',
            1:'LsiLogic',
            4:'PIIX3',
            8:'LsiLogicSas',
            0:'Null',
            2:'BusLogic',
            7:'I82078'
        }

        #NetworkAttachmentType状态类型字典
    NetworkAttachmentType_dict={
                6:'NATNetwork',
                5:'Generic',
                3:'Internal',
                4:'HostOnly',
                2:'Bridged',
                0:'Null'
        }
        #NetworkAdapterType状态类型字典
    NetworkAdapterType_dict={
            3:'I82540EM',
            6:'Virtio',
            2:'Am79C973',
            4:'I82543GC',
            5:'I82545EM',
            0:'Null'
        }

    def go(self,x):
            return x.LaunchVMProcess(self.session,"gui",'')

    def lock(self,x):
            x.LockMachine(self.session,self.vboxCnst.LockType_Write)
            return self.session.Machine

    def unlock(self,x):
            self.session.UnlockMachine()
            print('%s is unlock') %(x.Name)







    #查询物理机操作系统
    #返回值:操作系统名称(str),操作系统版本(str)
    def get_host_osversion(self,listset):
        try:
            result=['success',listset[0],self.host.OperatingSystem,self.host.OSVersion]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #物理机CPU信息
    #返回值:CPU描述信息(str),CPU物理核心数(int),CPU逻辑核心数(int)
    def get_host_cpuinfo(self,listset):
        try:
            result=['success',listset[0],self.host.GetProcessorDescription(0),self.host.ProcessorCoreCount,self.host.ProcessorCount]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #物理机CPU使用情况(保留改进)(需使用psutil模块)(待转换为监控线程)
    #返回值:CPU使用率(float)
    def get_host_cpu_usage(self,listset):
        try:
            result=['success',listset[0],psutil.cpu_percent(0)]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #物理机内存总大小
    def get_host_memsize(self,listset):
        try:
            result=['success',listset[0],self.host.MemorySize]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #物理机内存可用大小(待转换为监控线程)
    def get_host_mem_avail(self,listset):
        try:
            result=['success',listset[0],self.host.MemoryAvailable]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #vbox虚拟机文件所在磁盘分区使用情况(需使用psutil模块)(待转换为监控线程)
    #返回值:分区总大小/MB(long),分区使用大小/MB(long),分区使用百分率(float),VboxMachine相关文件所占空间大小/KB(long)
    def get_host_storageinfo(self,listset):
        try:
            diskinfo=psutil.disk_usage((os.getenv('VBOX_MSI_INSTALL_PATH'))[:2])
            vboxtotalsize = 0L
            for root, dirs, files in os.walk((os.getenv('VBOX_MSI_INSTALL_PATH'))[:2]+r'\VboxMachine'):
                vboxtotalsize += sum([getsize(join(root, name)) for name in files])
            result=['success',listset[0],diskinfo.total/1024/1024,diskinfo.used/1024/1024,diskinfo.percent,vboxtotalsize/1024]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #查询物理机上运行的所有虚拟机名称
    #返回值:虚拟机名称(str)*N
    def get_guest_list(self,listset):
        try:
            result=['success',listset[0],]
            machine_list=self.vbox.GetMachinesByGroups(('',))
            if machine_list is None:
                result.append(listset[len(listset)-1])
                return result
            else:
                for vm in machine_list:
                    result.append(vm.Name)
                result.append(listset[len(listset)-1])
                return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #查询虚拟机CPU分配情况
    #返回值:虚拟机CPU逻辑核心分配个数(int)
    def get_guest_cpucount(self,listset):
        try:
            result=['success',listset[0],listset[1],(self.vbox.FindMachine(listset[1])).CPUCount]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result


    #查询虚拟机电源状态
    #返回值:虚拟机状态(str)
    def get_guest_powerstate(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1],Imachine.State]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    # #获取虚拟机名称
    # #返回值:虚拟机名称(str)
    # def get_guest_name(self,listset):
    #     try:
    #         Imachine=self.vbox.FindMachine(listset[1])
    #         result=('success',Imachine.Name)
    #         return result
    #     except BaseException,e:
    #         result=('failure',str(e))
    #         print(str(e))
    #         return result

    #查询虚拟机操作系统
    #返回值:虚拟机操作系统名称(str)
    def get_guest_osversion(self,listset):
        try:
             Imachine=self.vbox.FindMachine(listset[1])
             result=['success',listset[0],listset[1],Imachine.OSTypeId]
             result.append(listset[len(listset)-1])
             return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机引导顺序
    #返回值:长度为4的启动项目(str)
    def get_guest_bootorder(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1],]
            for i in range(1,5):
                result.append(Imachine.GetBootOrder(i))
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机显存大小
    #返回值:虚拟机显存大小/MB(int)
    def get_guest_vramsize(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1],Imachine.VRAMSize]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机内存大小
    #返回值:虚拟机内存大小/MB(int)
    def get_guest_memsize(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1],Imachine.MemorySize]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机存储控制器对象信息
    #返回值:虚拟机存储控制器对象信息(list)
    #结构:[VM_Name(str),SC_Name(str),Bus(int)(搭配常数字典StorageBus),ControllerType(int)(搭配常数字典StorageControllerType),useHostIOCache(bool)]
    def get_guest_storagectrls(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            sc_list=Imachine.StorageControllers
            result=['success',listset[0],listset[1],]
            #result列表内,每4个元素分别存放一个StorageController对象的信息.如此循环
            for sc in sc_list:
                result.append(sc.Name)
                result.append(sc.Bus)
                result.append(sc.ControllerType)
                result.append(sc.UseHostIOCache)
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机存储媒体介质与存储控制器附加关系(list)
    #返回值:虚拟机存储媒体介质与存储控制器附加关系对象信息(list)
    #参数结构:[name(str)(StorageController.name)]
    #结构:[VM_Name,SC_name(str)(StorageController.name),Med_name(str)(medium.name),port(int),device=0(int),type(int)(搭配常数字典DeviceType)]
    def get_guest_mediumattachmen(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            ma_list=Imachine.GetMediumAttachmentsOfController(listset[2])
            result=['success',listset[0],listset[1]]
            #result列表内,每5个元素分别存放一个MediumAttachment对象的信息.如此循环
            for ma in ma_list:
                result.append(ma.Controller)
                if ma.Medium is not None:
                    result.append(ma.Medium.Name)
                else:
                     result.append(None)
                result.append(ma.Port)
                result.append(ma.Device)
                result.append(ma.Type)
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机存储媒体介质(medium)对象信息
    #返回值:虚拟机存储媒体介质(medium)对象信息(list)
    #结构:[name(str),format(str),DeviceType(int)(搭配常数字典DeviceType),size(long,Byte),logicalSize(long,Byte)]
    def get_guest_mediums(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            ma_list=Imachine.GetMediumAttachmentsOfController(listset[2])
            result=['success',listset[0],listset[1],]
            #result列表内,每5个元素分别存放一个Medium对象的信息.如此循环
            for ma in ma_list:
                if ma.Medium is not None:
                    result.append(ma.Medium.Name)
                    result.append(ma.Medium.Format)
                    result.append(ma.Medium.DeviceType)
                    result.append(ma.Medium.Size)
                    result.append(ma.Medium.LogicalSize)
            result.append(listset[len(listset)-1])
            print('Medium')
            print(result)
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #查询虚拟机网络适配器信息
    #返回值:虚拟机网络适配器对象信息(list
    #结构:[slot(long),enabled(int 1/0),MACAddress(str),attachmentType(int)(需搭配常数字典NetworkAttachmentType),BridgedInterface(str),adapterType(int)(需搭配常数字典NetworkAdapterType),cableConnected(bool)]
    def get_guest_networkadapters(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1]]
             #result列表内,每6个元素分别存放一个NetworkAdapter对象的信息.如此循环
            for i in range(0,8):
                na=Imachine.GetNetworkAdapter(i)
                result.append(na.Slot)
                result.append(na.Enabled)
                result.append(na.MACAddress)
                result.append(na.AttachmentType)
                result.append(na.BridgedInterface)
                result.append(na.AdapterType)
                result.append(na.CableConnected)
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #查询虚拟机共享文件夹信息
    #返回值:虚拟机共享文件夹对象信息(list)
    #结构:[name(str),HostPath(str),Writable(bool)]
    def get_guest_sharedfolders(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            sf_list=Imachine.SharedFolders
            result=['success',listset[0],listset[1],]
            #result列表内,每3个元素分别存放一个SharedFolder对象的信息.如此循环
            for sf in sf_list:
                result.append(sf.Name)
                result.append(sf.HostPath)
                result.append(sf.Writable)
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机描述性信息
    #返回值:虚拟机描述性信息(str)
    def get_guest_description(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            result=['success',listset[0],listset[1],Imachine.Description]
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #查询虚拟机性能信息
    #返回值:虚拟机性能信息(list)
    #结构:
    def get_guest_performance(self,listset): #OK
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            LocalPercol=self.vbox.PerformanceCollector
            LocalPercol.SetupMetrics(None,(Imachine,),2,5)
            CPU_Load=(LocalPercol.QueryMetricsData(('Guest/CPU/Load/User',),(Imachine,))[0])[1]
            #内存数据单位为KB
            Mem_Free=(LocalPercol.QueryMetricsData(('Guest/RAM/Usage/Free',),(Imachine,))[0])[1]
            Mem_Usage=(Imachine.MemorySize-Mem_Free/1024)*100/Imachine.MemorySize
            return ['success',listset[0],listset[1],CPU_Load/10000,Mem_Usage,listset[len(listset)-1]]
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result


    #新建虚拟机
    #listset中的参数定义为:[Name(str),Description(str),GuestOSTypes(str),MemSize/MB(int),VRAMSize/MB(int),VdiskName(str),VdiskSize/Byte(long)]
    #无返回
    def create_new_machine(self,listset):
        try:
            #使用ComposeMachineFilename组建VboxMachine所在目录的绝对路径,为安装Vbox的磁盘下的VboxMachine\[虚拟机名称]\[虚拟机名称].vbox
            settingfilepath=self.vbox.ComposeMachineFilename(listset[1],'',None,(self.VboxInstallPath)[:2] + '\\VboxMachine')
            #创建虚拟机,返回对应的Machine的类对象
            Imachine=self.vbox.CreateMachine(settingfilepath,listset[1],None,listset[3],"")
            #注册虚拟机
            self.vbox.RegisterMachine(Imachine)
            #组建虚拟磁盘文件所在目录
            VMFolder_Path =(settingfilepath)[:-(len(Imachine.Name)+5)]
            #创建medium对象
            Imedium=self.vbox.CreateHardDisk('vdi',VMFolder_Path+listset[6]+'.vdi')
            #使用medium对象创建虚拟磁盘
            Imedium.CreateBaseStorage(int(listset[7]),(self.vboxCnst.MediumVariant_Standard,))
            #-------锁定虚拟机开始添加存储控制器--------
            Imachine_mutable=self.lock(Imachine)
            #默认只添加一个SATA存储控制器,名称为SATA
            storagecontroller=Imachine_mutable.AddStorageController('SATA',self.vboxCnst.StorageBus_SATA)
            #开始附加媒体介质对象(Medium),使用'SATA'存储控制器的port:0
            Imachine_mutable.AttachDevice('SATA',0,0,self.vboxCnst.DeviceType_HardDisk,Imedium)
            #开始创建虚拟机光驱,使用'SATA'存储控制器的port:1
            Imachine_mutable.AttachDeviceWithoutMedium('SATA',1,0,self.vboxCnst.DeviceType_DVD)
            #开始修改虚拟机使用的物理内存大小/MB
            Imachine_mutable.MemorySize=int(listset[4])
            Imachine_mutable.VRAMSize=int(listset[5])
            #添加默认虚拟机共享文件夹,文件夹目录为安装Vbox的磁盘下的VboxMachine\[虚拟机名称]\'[虚拟机名称]_Shared'
            SF_Path=VMFolder_Path+Imachine_mutable.Name+'_Shared'
            if os.path.isdir(SF_Path)==False:
                os.mkdir(SF_Path)
            Imachine_mutable.CreateSharedFolder('SharedFolder',SF_Path,True,True)
            Imachine_mutable.Description=listset[2]
            #修改结束,保存配置
            Imachine_mutable.SaveSettings()
            #最后解锁虚拟机
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            self.del_machine(listset)
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #设定虚拟机名称
    #返回值:无
    def set_guest_name(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.Name=listset[2]
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机虚拟机操作系统
    #返回值:无
    def set_guest_osversion(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.OSTypeId=listset[2]
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机描述性信息
    #返回值:无
    def set_guest_description(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.Description=listset[2]
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机内存大小/MB
    #返回值:无
    def set_guest_memsize(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.MemorySize=int(listset[2])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机启动顺序
    #返回值:无
    def set_guest_bootorder(self,listset):
         try:
             Imachine=self.vbox.FindMachine(listset[1])
             Imachine_mutable=self.lock(Imachine)
             for i in range(1,5):
                 Imachine_mutable.SetBootOrder(i,int(listset[i+1]))
             Imachine_mutable.SaveSettings()
             self.unlock(Imachine)
             return ['success',listset[0],listset[1],listset[2],listset[3],listset[4],listset[5],listset[len(listset)-1]]
         except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],listset[3],listset[4],listset[5],str(e)]
            print(str(e))
            return result

    #设定虚拟机CPU分配情况
    #返回值:无
    def set_guest_cpucount(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.CPUCount=int(listset[2])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #查询虚拟机处理器使用峰值
    #返回值:虚拟机最大使用百分比(int)
    def get_guest_cpuexecutioncap(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            return ['success',listset[0],listset[1],Imachine.CPUExecutionCap,listset[len(listset)-1]]
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #设定虚拟机处理器使用峰值
    #返回值:无
    def set_guest_cpuexecutioncap(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.CPUExecutionCap=int(listset[2])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机显存大小
    #返回值:无
    def set_guest_vramsize(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            Imachine_mutable.VRAMSize=int(listset[2])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],str(e)]
            print(str(e))
            return result

    #设定虚拟机存储控制器对象信息
    #返回值:无
    #参数结构:[VM_Name(str),SC_Name(str),ControllerType(int)(搭配常数字典StorageControllerType),useHostIOCache(int)]
    def set_guest_storagectrls(self,listset):
        #useHostIOCache的值int类型 1/0)
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            sc=Imachine_mutable.GetStorageControllerByName(listset[2])
            sc.ControllerType=int(listset[3])
            sc.UseHostIOCache=int(listset[4])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[3],listset[4],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #设定虚拟机网络适配器信息
    #返回值:无
    #参数结构:[VM_name(str),slot(long),enabled(int 1/0),MACAddress(str),attachmentType(int)(需搭配常数字典NetworkAttachmentType),BridgedInterface(str),adapterType(int)(需搭配常数字典NetworkAdapterType),cableConnected(bool)]
    def set_guest_networkadapters(self,listset):
        #CableConnected的类型假设为int,有效值为1,0
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            na=Imachine_mutable.GetNetworkAdapter(int(listset[2]))
            na.Enabled=int(listset[3])
            na.MACAddress=listset[4]
            na.AttachmentType=int(listset[5])
            na.bridgedInterface=listset[6]
            na.AdapterType=int(listset[7])
            na.CableConnected=int(listset[8])
            Imachine_mutable.SaveSettings()
            self.unlock(Imachine_mutable)
            return ['success',listset[0],listset[1],listset[2],listset[3],listset[4],listset[5],listset[6],listset[7],listset[8],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],listset[2],listset[3],listset[4],listset[5],listset[6],listset[7],listset[8],str(e)]
            print(str(e))
            return result

    #获取宿主机网络适配器信息 (单名称,只用于设定虚拟机网络适配器的桥接接口名称)
    #返回值:宿主机网络适配器名称(list)
    def get_host_networkadapters(self,listset):
        try:
            result=['success',listset[0],]
            for interface in self.wmi_obj.Win32_NetworkAdapterConfiguration(IPEnabled=1):
                result.append(interface.Description)
            return result
        except BaseException,e:
            result=['failure',listset[0],str(e)]
            print(str(e))
            return result

    #添加虚拟机使用的ISO文件作为Medium,ISO文件来自于FTP文件夹
    #返回值:无
    #参数结构:[VM_Name(str),SC_Name(str),Port(long),ISOFileName(str)]
    def add_guest_mediums_dvd(self,listset):#OK
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            Imachine_mutable=self.lock(Imachine)
            ISO_path=(self.VboxInstallPath)[:2] + '\\VboxMachine\\ISO'
            if os.path.isdir(ISO_path)==False:
                os.mkdir(ISO_path)
            shutil.move(self.FtpPath+'\\'+listset[4],ISO_path+'\\'+listset[4])
            ma=Imachine_mutable.GetMediumAttachment(listset[2],int(listset[3]),0)
            if ma.Medium is None:
                Mediunm_DVD=self.vbox.OpenMedium(ISO_path+'\\'+listset[4],self.vboxCnst.DeviceType_DVD,self.vboxCnst.AccessMode_ReadOnly,True)
                Imachine_mutable.MountMedium(listset[2],int(listset[3]),0,Mediunm_DVD,True)
            else:
                med_dvd_old=Imachine_mutable.GetMedium(listset[2],int(listset[3]),0)
                Imachine_mutable.UnmountMedium(listset[2],int(listset[3]),0,True)
                med_dvd_old_Name=med_dvd_old.Name
                med_dvd_old.DeleteStorage()
                med_dvd_old.Close()
                Mediunm_DVD=self.vbox.OpenMedium(ISO_path+'\\'+listset[4],self.vboxCnst.DeviceType_DVD,self.vboxCnst.AccessMode_ReadOnly,True)
                Imachine_mutable.MountMedium(listset[2],int(listset[3]),0,Mediunm_DVD,True)
                self.unlock(Imachine)
            return ['success',listset[0],listset[1],listset[2],listset[len(listset)-1]]
        except BaseException,e:
            if self.session.State==2:
                self.unlock(Imachine)
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #删除虚拟机
    #返回值:无
    def del_machine(self,listset):
        try:
            Imachine=self.vbox.FindMachine(listset[1])
            med_list=Imachine.Unregister(self.vboxCnst.CleanupMode_Full)
            for med in med_list:
                med.DeleteStorage()
                med.Close()
            shutil.rmtree((Imachine.SettingsFilePath)[:-len(Imachine.Name)-6])
            Imachine.DeleteConfig(med_list)

            return['success',listset[0],listset[1],listset[len(listset)-1]]
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #启动虚拟机,默认先使用对应session的Console对象的PowerOn方法启动,如为对象为None,则使用Machine对象的LaunchVMProcess方法
    #返回值:启动之后新增运行的所有VirtualBox.exe进程对应的PID
    #注意:只有安装有操作系统的虚拟机才能使用Console对象进行模拟电源操作
    def machine_poweron(self,listset):
        try:
            #如果因为不能使用Console对象而无法进行关机则需要使用强制结束进程的方法,所以在开机时需要查询开机后对应的VirtualBox.exe进程的PID号
            #查询运行虚拟机前已有的VirtualBox.exe进程的PID号
            p_list=psutil.get_process_list()
            Old_VirtualBoxPidSet=[]
            for p in p_list:
                str_p=str(p)
                pid_re=re.compile('VirtualBox',re.I)
                if pid_re.search(str_p):
                    Old_VirtualBoxPidSet.append(str_p.split('pid=')[1].split(',')[0]  )
            Old_VirtualBoxPidSet=set(Old_VirtualBoxPidSet)
            #开始启动虚拟机
            Imachine=self.vbox.FindMachine(listset[1])
            LocalSession=client.Dispatch("VirtualBox.Session")
            Imachine.LockMachine(LocalSession,self.vboxCnst.LockType_Write)
            #把Localsession储存至类中的session字典中,以虚拟机名字为值
            self.SessionDict[listset[1]]=LocalSession
            Imachine_mutable=LocalSession.Machine
            MachineConsole=LocalSession.Console
            if MachineConsole is not None:
                MachineConsole.PowerUp()
            else:
                LocalSession.UnlockMachine()
                Imachine.LaunchVMProcess(LocalSession,"gui",'')
            #虚拟机启动完成
            #查询运行虚拟机后所有的VirtualBox.exe进程的PID号
            p_list=psutil.get_process_list()
            New_VirtualBoxPidSet=[]
            for p in p_list:
                str_p=str(p)
                pid_re=re.compile("VirtualBox.exe",re.I)
                if pid_re.search(str_p):
                    New_VirtualBoxPidSet.append(str_p.split('pid=')[1].split(',')[0]  )
            New_VirtualBoxPidSet=set(New_VirtualBoxPidSet)
            #集合相减,得到此次运行虚拟机而产生的VirtualBox.exe的进程的PID号
            PID_List=New_VirtualBoxPidSet-Old_VirtualBoxPidSet
            result=['success',listset[0],listset[1],]
            for pid in PID_List:
                result.append(pid)
            result.append(listset[len(listset)-1])
            return result
        except BaseException,e:
            result=['failure',listset[0],listset[1],str(e)]
            print(str(e))
            return result

    #关闭虚拟机,默认先使用对应session的Console对象的PowerOn方法启动,如为对象为None,则直接根据提供的PID号结束对应进程
    #返回值:无
    def machine_poweroff(self,listset):
        try:
            if listset[1] in self.SessionDict:
                LocalSession = self.SessionDict[listset[1]]
                MachineConsole = LocalSession.Console
                if MachineConsole is not None:
                    MachineConsole.PowerDown()
                else:
                    for i in range(2, len(listset)-1):
                        if psutil.pid_exists(int(listset[i])):
                            os.kill(int(listset[i]), 9)
            else:
                for i in range(2, len(listset)-1):
                    if psutil.pid_exists(int(listset[i])):
                        os.kill(int(listset[i]), 9)
            return ['success', listset[0], listset[1],listset[len(listset)-1]]
        except BaseException, e:
            result = ['failure', listset[0], listset[1], str(e)]
            print(str(e))
            return result





    #关键字对应方法字典
    function_dict={
        'GET_HOST_OSVERSION':get_host_osversion,
        'GET_HOST_CPUINFO':get_host_cpuinfo,
        'GET_HOST_CPU_USAGE':get_host_cpu_usage,
        'GET_HOST_MEMSIZE':get_host_memsize,
        'GET_HOST_MEM_AVAIL':get_host_mem_avail,
        'GET_HOST_STORAGEINFO':get_host_storageinfo,
        'GET_GUEST_LIST':get_guest_list,
        'GET_GUEST_POWERSTATE':get_guest_powerstate,
        'GET_GUEST_CPUCOUNT':get_guest_cpucount,
        'SET_GUEST_CPUCOUNT':set_guest_cpucount,
        'GET_GUEST_CPUEXECUTIONCAP':get_guest_cpuexecutioncap,
        'SET_GUEST_CPUEXECUTIONCAP':set_guest_cpuexecutioncap,
        'GET_GUEST_VRAMSIZE':get_guest_vramsize,
        'SET_GUEST_VRAMSIZE':set_guest_vramsize,
        'GET_GUEST_MEMSIZE':get_guest_memsize,
        'SET_GUEST_MEMSIZE':set_guest_memsize,
        'GET_GUEST_PERFORMANCE':get_guest_performance,
        'SET_GUEST_NAME':set_guest_name,
        'GET_GUEST_OSVERSION':get_guest_osversion,
        'SET_GUEST_OSVERSION':set_guest_osversion,
        'GET_GUEST_BOOTORDER':get_guest_bootorder,
        'SET_GUEST_BOOTORDER':set_guest_bootorder,
        'GET_GUEST_STORAGECTRLS':get_guest_storagectrls,
        'SET_GUEST_STORAGECTRLS':set_guest_storagectrls,
        'GET_GUEST_MEDIUMATTACHMEN':get_guest_mediumattachmen,
        # 'SET_GUEST_MEDIUMS':set_guest_mediums,(待定)
        'GET_GUEST_MEDIUMS':get_guest_mediums,
        'GET_GUEST_NETWORKADAPTERS':get_guest_networkadapters,
        'SET_GUEST_NETWORKADAPTERS':set_guest_networkadapters,
        'GET_HOST_NETWORKADAPTERS':get_host_networkadapters,
        'GET_GUEST_SHAREDFOLDERS':get_guest_sharedfolders,
        # 'ADD_GUEST_SHAREDFOLDERS':add_guest_sharedfolders,(待定)
        # 'REMOVE_GUEST_SHAREDFOLDERS':remove_guest_sharedfolders,(待定)
        'ADD_GUEST_MEDIUMS_DVD':add_guest_mediums_dvd,
        'DEL_MACHINE':del_machine,
        'CREATE_NEW_MACHINE':create_new_machine,
        'GET_GUEST_DESCRIPTION':get_guest_description,
        'SET_GUEST_DESCRIPTION':set_guest_description,
        'MACHINE_POWERON':machine_poweron,
        'MACHINE_POWEROFF':machine_poweroff,
        }


    def vbox_funcation(self,commandlist):
        commandlist=tuple(commandlist)
        print('-------------------------')
        print(type(commandlist))
        print(commandlist)
        return self.function_dict[commandlist[0]](self,commandlist)












