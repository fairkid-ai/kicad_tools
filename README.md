
# KiCad EDA 生产文件生成器

现已支持KiCad 6.0. 当直接从PCB更新原理图时，生成的BOM表会缺少Datasheet信息，解决办法，在原理图中生成网表。

Not support KiCad 6.0. When update PCB from schematic directly, datasheet field will miss. Generate netlist in schematic to solve it.

与JLCPCB和JLCKicadTools不同的是，这个工具只根据已有的器件信息来生成生产文件，不会调整器件的角度或是元件号。因此要求在设计原理图和使用封装的时候使用jlc.com上的器件信息，才能保证生成的文件能直接在jlc.com中制作。
* 一些常用的jlc.com器件库[lc_kicad_lib](https://github.com/xtoolbox/lc_kicad_lib)
* 或者是直接从lceda.cn中复制器件和封装库[lckiconverter](https://github.com/xtoolbox/lckiconverter)

Unlike JLCPCB and JLCKicadTools, this tool only generates fabrication files based on existing device information and does not adjust the angle or part number of the device. Therefore, it is required to use the component and footprint in jlc.com when designing the schematic and PCB to ensure that the generated file can be directly used at jlc.com.
* Some common used jlc.com library[lc_kicad_lib](https://github.com/xtoolbox/lc_kicad_lib)
* Get KiCad symobl/footprint from lceda.cn [lckiconverter](https://github.com/xtoolbox/lckiconverter)

## 中文说明

本插件可一键生成 PCB 的 Gerber、钻孔、BOM 物料清单、坐标文件。

### 安装

适用于：KiCad EDA 5.1.0 +

* Windows 安装命令
    ```
    git clone https://github.com/xtoolbox/kicad_tools.git %appdata%/kicad/scripting/plugins/kicad_tools
    ```
* Linux 安装命令
    ```
    // TODO
    ```

### 使用

安装完成即可使用，找到 `工具` -> `外部插件` -> `Gen Manufacture Docs` 打开插件界面，点击插件界面上的 `Gen Manufacture Docs ` 按钮执行命令。

![desc](desc.png)

### 生成文件

当 `BOM List` `Positon File` `Gerber Files` 全选时，点击 `Generate Marnufacture Docs` 按钮后插件会一键生成 BOM 物料清单、坐标文件、Gerber 文件、钻孔文件。

BOM 文件和坐标文件会以 CSV 格式存放在电路板同级目录下，Gerber 和钻孔文件放在电路板目录下的 gerber 目录中，通过 `Split Slot` 选项生成的钻孔文件中的槽孔会被转换成多个普通孔。

生成的文件可以直接在 sz-jlc.com 进行贴装。

### 注意事项

GenMFDoc() 会改变电路板的钻孔原点，建议先用GenMFDoc() 生成 BOM 清单和位置文件，再生成 Gerber 文件。

### 参考

KiCad plot tool is forked from "https://github.com/blairbonnett-mirrors/kicad/blob/master/demos/python_scripts_examples/gen_gerber_and_drill_files_board.py"


# Manufacture Tools for kicad

Usage:

step 1: Copy the mf_tool.py gerber_drill.py loadnet.py and sexpdata.pyto “[kicad install path]\share\kicad\scripting\plugins”

step 2: In Python console window, type 
```python
import mf_tool as mf
mf.GenSMTFiles()
```

step 3: or in [tools]->[external tools] menu, invoke the [Gen Manufacture Docs] command.

step 4: the BOM and Postion CSV file will be generated under the same folder of the board file。 Gerber and drill file is under the "gerber" folder. The slot hole in drill file will split to hole serires. Send them to jlcpcb.com to get a PCBA.

## Attention:

The GenMFDoc() command will change the Aux original point

## Preivew


![holes_with_ref](holes_with_ref.png)


![slot_without_ref](slot_without_ref.png)
