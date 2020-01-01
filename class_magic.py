#Generate class structures based on vftable data
#@author buherator
#@category _NEW_
#@keybinding 
#@menupath 
#@toolbar 

from ghidra.program.model.data import Array, CategoryPath, PointerDataType, StructureDataType, DataTypeConflictHandler
from ghidra.program.model.symbol import SourceType
import re

def createVftableType(namespace, length):
    dtm = currentProgram.getDataTypeManager()
    programName = getProgramFile().getName()
    categoryPath="/%s" % ('/'.join(namespace.split("::")[:-1]))
    #category=dtm.createCategory(CategoryPath(categoryPath))
    structDataType=StructureDataType(CategoryPath(categoryPath), "%s_vftable" % namespace.split('::')[-1], 0)
    dt=dtm.addDataType(structDataType, DataTypeConflictHandler.REPLACE_HANDLER)
    for i in range(0,length):
        p=PointerDataType()
        dt.add(p, currentProgram.getDefaultPointerSize(), "member%X" % (i),"")
    return dt

def createClassType(namespace, vftableDataType):
    dtm = currentProgram.getDataTypeManager()
    categoryPath="/%s" % ('/'.join(namespace.split("::")[:-1]))
    #structDataType=StructureDataType(CategoryPath(categoryPath), namespace.split('::')[-1], 0)
    structDataType=StructureDataType(CategoryPath(categoryPath), namespace, 0)
    dt=dtm.addDataType(structDataType, DataTypeConflictHandler.REPLACE_HANDLER)
    p=PointerDataType(vftableDataType)
    dt.add(p, currentProgram.getDefaultPointerSize(), "fvtable","")
    return dt

vftable_re=re.compile('const ([a-zA-Z:_-]+)::vftable$')

currAddr = currentLocation.getAddress()
vftable_comment=getPlateComment(currAddr)

class_match=vftable_re.match(vftable_comment)
class_namespace=None
if class_match is not None:
    class_namespace = class_match.group(1)
else:
    print("[!] Class namespace not found!")
    exit()

originalData=getDataAt(currAddr)
originalDataType=originalData.getDataType()
newVftableDataType = None
newClassDataType = None
if isinstance(originalDataType, Array):
    newVftableDataType=createVftableType(class_namespace, originalDataType.getNumElements())
    removeDataAt(currAddr)
    createData(currAddr, newVftableDataType)
    newClassDataType=createClassType(class_namespace, newVftableDataType)
    classNS=currentProgram.getSymbolTable().createClass(None, class_namespace, SourceType.USER_DEFINED)
    for i in range(0,originalDataType.getNumElements()*currentProgram.getDefaultPointerSize(), currentProgram.getDefaultPointerSize()):
        funcAddr=None
        # Ugly hack to get properly sized pointers
        if currentProgram.getDefaultPointerSize() == 4:
            funcAddrStr=hex(getInt(currAddr.add(i))).strip('L')
        if currentProgram.getDefaultPointerSize() == 8:
            funcAddrStr=hex(getLong(currAddr.add(i))).strip('L')
        funcAddr=getAddressFactory().getAddress(funcAddrStr)
	f=getFunctionAt(funcAddr)
        if f is not None:
            origName=f.getName()
            f.setParentNamespace(classNS)
        else:
            print("[!] not a function at %x" % funcAddr.getOffset())
else:
    print("[!] Not an array")
    exit()



