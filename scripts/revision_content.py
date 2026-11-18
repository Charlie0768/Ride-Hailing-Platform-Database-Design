"""Restore the original report's diagram-to-SQL presentation sequence."""
import json,re

def revise(P,R,table,code,esc):
 E=json.loads((R/'results/report_evidence.json').read_text())
 def plate(name):return '\\clearpage\n\\includepdf[pages=1,fitpaper=true,pagecommand={\\thispagestyle{empty}}]{figures/'+name+'.pdf}\n'
 def sample(key,cols=None):
  item=E[key];rows=item['rows'];cols=cols or list(rows[0])
  sql=item['sql'];sql=re.sub(r' FROM ',r'\nFROM ',sql);sql=re.sub(r' ORDER BY ',r'\nORDER BY ',sql)
  return (r'\par\noindent\begin{minipage}{\linewidth}\setlength{\parskip}{0pt}\renewcommand{\arraystretch}{1.08}\titlespacing*{\subsection}{0pt}{7pt}{4pt}\lstset{aboveskip=4pt,belowskip=4pt}'+'\n'+ '\\subsection*{'+esc(key)+'}\n'+code(sql)+table(cols,[[row[c] for c in cols] for row in rows])+r'\end{minipage}\par\vspace{5pt}'+'\n')
 functional=('Front-end and back-office functions','前台与后台功能结构',
 '''The next two diagrams restore the functional decomposition of the original design. Passenger and driver services are separated on the front end; identity, assets, operations, finance and location are organized on the back end. These are requirement diagrams, not screenshots of an implemented application.

Solid boxes identify functions supported by the implemented database. Gray boxes preserve related services from the initial business description while marking them as external or future work. Registration records are stored, but login authentication is not implemented. Fare records and summaries are implemented, but payment execution and settlement are not. Driver identity is recorded, while formal eligibility review remains external.

This scope distinction prevents the diagrams from promising functionality absent from the schema. It also preserves the broader ride-hailing context without expanding the current database beyond its 11 core tables.''',
 '''后两张图恢复原稿中的功能分解：前台按乘客、司机划分，后台按身份、资产、运营、财务与位置服务组织。这些是需求分析图，不是已经开发完成的应用界面截图。

实线功能框表示数据库支持的功能，灰色框保留原业务描述中的关联服务，同时标明它们属于外围系统或后续扩展。数据库保存注册记录，但没有实现登录认证；保存费用与汇总，但没有实现支付执行和结算；记录司机身份，但正式准入审核仍在系统范围之外。

这样既保留网约车业务背景，也避免图中承诺数据库没有实现的功能，并控制在现有 11 张核心表的范围内。''',plate('01_frontend')+plate('02_backend'))
 concept=('Complete conceptual ER/EER model','完整概念 ER/EER 模型',
 '''The following full-size plate uses the notation taught in LN3 and LN4. Entities are rectangles, attributes are ellipses, identifiers are underlined, relationships are diamonds, and minimum/maximum cardinalities are shown with circles, bars and crow feet. DriverShift, Review and Surcharge are identification-dependent entities and use double rectangles. Double diamonds make their identifying relationships explicit; LN3 notes that the distinction between ordinary and identifying relationship diamonds is not compulsory in the course.

The two specialization circles are marked o for overlapping user roles and d for disjoint trip outcomes. A single line from the supertype denotes partial specialization. Subtypes inherit the parent identifier; it is not repeated as a separate oval. The partial identifier shift_start has a dashed underline. DriverShift is identified jointly by its driver and that start time. Review and Surcharge have no additional partial identifier because each completed trip has at most one of each.

All non-inherited conceptual attributes are shown. Foreign-key columns introduced by relational mapping are shown in the separate relational diagram, rather than duplicated as conceptual attributes. InsurancePolicy has its own globally unique identifier and is not treated as a weak entity. Lines that cross without a junction dot do not create an additional relationship.''',
 '''后面的完整大图采用 LN3、LN4 的符号：矩形表示实体，椭圆表示属性，下划线表示标识符，菱形表示联系；基数用圆圈、竖线及乌鸦脚表达。DriverShift、Review、Surcharge 的身份依赖其所有者，使用双矩形；双菱形明确表示识别联系。LN3 同时说明课程并不强制区分普通联系和识别联系的菱形样式。

两个特化圆分别用 o 表示用户角色可重叠，用 d 表示行程结果互斥。父实体到特化圆的单线表示部分特化。子类继承父实体标识符，不额外重复画成椭圆。shift_start 使用虚线下划线表示局部标识符，轮班通过司机和开始时间共同识别。评价和附加费每单最多一条，因此不需要另一个局部标识符。

图中显示全部非继承的概念属性。关系转换阶段引入的外键列在后面的关系图展示，避免在概念层重复画作普通属性。InsurancePolicy 有独立的全局唯一编号，不作为弱实体。没有连接圆点的线条交叉不表示新增联系。''',
 table(['Symbol','Meaning'],[['Rectangle / double rectangle','Regular entity / identification-dependent entity'],['Ellipse / underline','Attribute / entity identifier'],['Dashed underline','Partial identifier within an owner'],['Diamond / double diamond','Relationship / identifying relationship'],['Circle + bar; two bars','Zero or one; exactly one'],['Circle + crow foot','Zero or many'],['o / d in a circle','Overlapping / disjoint specialization'],['Single supertype connector','Partial specialization']])+plate('03_chen_eer'))
 relational=('Complete relational schema diagram','完整关系模式图',
 '''The following diagram is the implementation-level counterpart of the conceptual model. It includes every column of the 11 operational tables, with PK, FK and UQ markers and an explicit nullable marker. The column inventory is generated from the executed MySQL information_schema export. Table labels, columns and foreign-key endpoints therefore refer to the same database used by the SQL examples.

The role tables inherit AppUser's key. Outcome tables inherit Trip's key. Review and Surcharge use the CompletedTrip key as their own key; DriverShift combines the owner key with the partial identifier. The diagram also makes optional vehicle assignment visible through the nullable Trip.plate column.

Cardinalities describe structural possibilities. The lifecycle narrows these by status: an assigned or started trip needs a vehicle, and terminal status must agree with the matching detail table. These state-dependent constraints are implemented through the previously described checks, procedures and application privilege boundary.''',
 '''后面的关系图是概念模型的实现层对应图，展示全部 11 张运营表的所有字段，标明 PK、FK、UQ 及可空字段。字段清单根据实际 MySQL information_schema 导出结果生成，因此图中的表、字段和外键引用与 SQL 示例来自同一数据库。

角色表继承用户键，结果表继承行程键；评价与附加费以完成行程键作为自己的键；轮班由所有者键和局部标识符组合。Trip.plate 的可空标记也明确表达派车前的可选参与。

图上的基数表示结构上允许的关系，状态规则进一步收窄这些可能性：已派单或开始的行程必须有车辆，终态必须与结果子表对应。这些状态相关约束由 CHECK、过程和应用权限共同保证。''',plate('04_relational'))
 ddl=('Creating the database and all core tables','创建数据库及全部核心表',
 '''The following listing reproduces the complete executed DDL for the 11 operational tables. It includes the database declaration, primary and alternate keys, foreign keys, domain constraints and indexes. CREATE TABLE order follows parent-before-child dependencies, so foreign-key checks remain enabled during construction.

InnoDB provides transactional tables. The script intentionally fails if the schema already exists. No application data are silently deleted to make a demonstration pass. The complete procedure and trigger definitions remain in the companion SQL file; the lifecycle section explains how they are used.''',
 '''下面直接列出实际执行的全部 11 张运营表的建表 SQL，包含建库语句、主键和备用键、外键、值域约束及索引。创建顺序遵循先父表后子表，不需要关闭外键检查。

所有表采用支持事务的 InnoDB。如果 schema 已存在，脚本会明确报错，不会为了运行演示而悄悄删除数据。过程和触发器的完整定义仍在配套 SQL 文件中，生命周期章节解释其作用。''',r'\lstinputlisting[language=SQL,basicstyle=\ttfamily\footnotesize]{sql/01_schema.sql}')
 inventory=('Displaying the created tables and structure','展示已创建的表与结构',
 '''SHOW TABLES verifies which objects actually exist after the build. The output includes 11 operational tables, four dw_ analytical tables and two views. DESCRIBE trip provides a second, independent view of the implemented columns. The selected output columns below are Field, Type, Null and Key; the full raw output is supplied with the evidence files.''',
 '''SHOW TABLES 展示建库后实际存在的对象：11 张运营表、4 张 dw_ 分析表和 2 个视图。DESCRIBE trip 进一步展示实际字段结构。下方选取 Field、Type、Null、Key 四列展示，完整原始输出在证据文件中。''',r'\noindent\begin{minipage}[t]{.29\linewidth}\vspace{0pt}'+sample('show_tables')+r'\end{minipage}\hfill\begin{minipage}[t]{.68\linewidth}\vspace{0pt}'+sample('describe_trip',['Field','Type','Null','Key'])+r'\end{minipage}')
 additions=[]
 for en,zh,keys,ep,zp in [
 ('Inserted data for users and roles','用户与角色的数据展示',['app_user','passenger','driver'],
 'These ordered SELECT queries show actual inserted rows. User 1 appears in both the passenger and driver tables, demonstrating overlapping specialization. The user sample shows selected identity columns; the complete column definitions remain in the data dictionary.',
 '以下按键排序的 SELECT 展示实际插入数据。用户 1 同时出现在乘客表和司机表中，体现可重叠特化。用户样例选取身份字段展示，完整字段定义见数据字典。'),
 ('Inserted data for assets and shifts','车辆保险与轮班的数据展示',['vehicle','insurance_policy','driver_shift'],
 'The rows below connect vehicles to their registered drivers and policies to vehicles. The shift sample includes two shifts for the same driver on one date, confirming why a date alone is not a sufficient partial identifier. These are synthetic records returned by MySQL, not manually typed expected results.',
 '下列数据展示车辆到司机、保单到车辆的关联。轮班样例包含同一司机在同一天的两个班次，说明仅用日期不足以作为局部标识符。这些合成记录由 MySQL 实际查询返回，并非手工填写的预期结果。'),
 ('Inserted data for trips and outcomes','行程与结果的数据展示',['trip','completed_trip','cancelled_trip'],
 'Trip stores the request and current state, while terminal detail tables store outcome-specific attributes. The Trip sample selects the identifiers, assignment, status and estimated fare to keep the table readable. SELECT * is used for the two detail samples. The entire dataset remains available in the seed SQL.',
 'Trip 保存请求及当前状态，终态详情保存对应结果的专属属性。为便于阅读，主表样例选取编号、派车、状态和预估费用；两种结果子表使用 SELECT *。完整数据在种子 SQL 中提供。'),
 ('Feedback, surcharge and joined results','评价附加费及连接查询结果',['review','surcharge','joined_example'],
 'The review sample displays both scores and their missing values. The surcharge table has rows only where an extra charge applies. The final LEFT JOIN combines trip status, actual vehicle, derived driver and total fare. Open or cancelled trips remain visible with a NULL total_fare because no completion record exists.',
 '评价样例展示双方评分及缺失值，附加费表只在确有附加费时存在记录。最后的 LEFT JOIN 把行程状态、实际车辆、派生司机及总费用联系起来。开放或取消行程仍保留在结果中，由于没有完成详情，其 total_fare 为 NULL。')]:
  additions.append((en,zh,ep,zp,''.join(sample(k) for k in keys)))
 crud=('Insertion, update and deletion with results','插入修改删除及实际结果',
 '''This disposable example demonstrates the three write operations and their observable results. A temporary user is inserted, renamed, then deleted. After each operation, a query captures the database state. The final count is zero; the record is not part of the published sample dataset. Deleting a referenced historical user is a separate negative test and is rejected by the foreign key.''',
 '''本例使用临时用户演示三种写操作及实际结果：先插入，再修改姓名，最后删除。每一步后都查询数据库状态。最终计数为 0，临时记录不属于发布的样例数据。删除被历史记录引用的用户属于另一项负向测试，会被外键拒绝。''',''.join(sample('crud_'+x) for x in ['insert','update','delete']))
 decisions=('Changes from the initial framework','与初始框架的对应调整',
 '''The project requirements do not require replacing the original diagram types or omitting SQL demonstrations. This report keeps that development sequence: functional decomposition, conceptual ER/EER, relational mapping, table creation, inserted data and executable queries. The model changes below are correctness and scope decisions, not additional requirements imposed by the specification.''',
 '''项目要求并没有要求替换原来的图类型，也没有要求省略 SQL 演示。本报告保留原稿的开发顺序：功能分解、概念 ER/EER、关系转换、创建表、插入数据和查询结果。下列模型调整来自正确性和范围控制，而不是项目说明新增的硬性要求。''',
 table(['Initial item','Current representation','Reason'],[
 ['Unfinished trip','Trip status plus CancelledTrip','Waiting and active trips have no cancellation time'],
 ['Driver and vehicle on trips','Trip.plate plus derived driver','Fixed ownership makes duplicate driver storage redundant'],
 ['Shift identified by driver/date','Driver plus shift_start','A driver can have multiple shifts on one date'],
 ['Independent review identifier','Completed trip identifier','One bilateral review record per completed trip'],
 ['Vehicle insurance treated as weak','Independent policy_id','The policy has its own globally unique identifier'],
 ['Payment, settlement and live maps','Gray external/future function boxes','Retain context without claiming unimplemented services']]))
 out=[]
 for item in P:
  name=item[0]
  if name=='Conceptual model':out.append(concept)
  else:out.append(item)
  if name=='Requirements and acceptance criteria':out.extend([functional,decisions])
  if name=='Mapping the model into relations':out.append(relational)
  if name=='SQL implementation and integrity':out.extend([ddl,inventory])
  if name=='Synthetic dataset and reproducibility':out.extend(additions)
  if name=='Validation results':out.append(crud)
 return out
