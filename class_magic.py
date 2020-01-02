#Generate class structures based on vftable data
#@author buherator
#@category _NEW_
#@keybinding 
#@menupath 
#@toolbar 

from ghidra.app.util import NamespaceUtils
from ghidra.program.model.data import Array, CategoryPath, PointerDataType, StructureDataType, DataTypeConflictHandler
from ghidra.program.model.listing import VariableUtilities, GhidraClass
from ghidra.program.model.symbol import SourceType

def createVftableType(namespace, length):
    dtm = currentProgram.getDataTypeManager()
    programName = getProgramFile().getName()
    categoryPath="/%s" % ('/'.join(namespace.getName(True).split("::")[:-1]))
    #category=dtm.createCategory(CategoryPath(categoryPath))
    structDataType=StructureDataType(CategoryPath(categoryPath), "%s_vftable" % namespace.getName(True).split('::')[-1], 0)
    dt=dtm.addDataType(structDataType, DataTypeConflictHandler.REPLACE_HANDLER)
    for i in range(0,length):
        p=PointerDataType()
        dt.add(p, currentProgram.getDefaultPointerSize(), "member%X" % (i),"")
    return dt

def createClassType(namespace, vftableDataType):
    dtm = currentProgram.getDataTypeManager()
    #structDataType=StructureDataType(CategoryPath(categoryPath), namespace.split('::')[-1], 0)
    p=PointerDataType(vftableDataType)
    structDataType = VariableUtilities.findOrCreateClassStruct(namespace, dtm)
    if structDataType.getComponent(0):
        structDataType.replace(0, p, currentProgram.getDefaultPointerSize(), "fvtable","")
    else:
        structDataType.add(p, currentProgram.getDefaultPointerSize(), "fvtable","")
    return structDataType

currAddr = currentLocation.getAddress()

originalData=getDataAt(currAddr)
originalDataType=originalData.getDataType()

class_namespace=None
if originalData:
    symbol = originalData.getPrimarySymbol()
    if symbol:
        class_namespace = symbol.getParentNamespace()

if not class_namespace:
    print("[!] Class namespace not found!")
    exit()

newVftableDataType = None
newClassDataType = None
if isinstance(originalDataType, Array):
    if not isinstance(class_namespace, GhidraClass):
        class_namespace = NamespaceUtils.convertNamespaceToClass(class_namespace)
    newVftableDataType=createVftableType(class_namespace, originalDataType.getNumElements())
    removeDataAt(currAddr)
    createData(currAddr, newVftableDataType)
    newClassDataType=createClassType(class_namespace, newVftableDataType)
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
            f.setParentNamespace(class_namespace)
        else:
            print("[!] not a function at %x" % funcAddr.getOffset())
else:
    print("[!] Not an array")
    exit()



