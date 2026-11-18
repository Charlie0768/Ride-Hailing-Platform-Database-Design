# -*- coding: utf-8 -*-
from pathlib import Path
import json,csv,collections
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'results/query_results.json').read_text())
V=json.loads((R/'results/validation.json').read_text())
def esc(x):
 return ''.join({'&':r'\&','%':r'\%','_':r'\_\allowbreak{}','#':r'\#','$':r'\$'}.get(c,c) for c in str(x))
def table(headers,rows,widths=None):
 n=len(headers);spec=widths or ({'ID':r'p{.8cm}p{5cm}Y','Area':r'p{2.5cm}Yp{1.5cm}'}.get(headers[0]) or 'Y'*n)
 return '\\par\\begingroup\\small\\noindent\n\\begin{tabularx}{\\linewidth}{'+spec+'}\n\\toprule\n'+' & '.join(map(esc,headers))+r'\\\midrule'+'\n'+'\n'.join(' & '.join(map(esc,row))+r'\\' for row in rows)+'\n\\bottomrule\n\\end{tabularx}\n\\par\\endgroup\n'
def result(name,cols,headers=None):return table(headers or cols,[[r[c] for c in cols] for r in D[name]])
def code(s):return '\\begin{lstlisting}\n'+s.strip()+'\n\\end{lstlisting}\n'
def paras(s):return '\n\n'.join(esc(x.strip()) for x in s.strip().split('\n\n'))+'\n\n'
P=[]
def page(en,zh,eng,ch,extra=''):
 P.append((en,zh,eng,ch,extra))
page('Purpose and business requirements','项目目的与业务需求',
'''A ride-hailing platform must relate a booking to its passenger, assigned vehicle, responsible driver and final outcome. This project builds a relational database for that operational record. It retains the original design's user roles, vehicles, insurance, shifts, trips and feedback, while making their keys, state rules and implementation consistent.

The primary users are passengers who request rides, drivers who serve them, and platform operators who inspect service records. The database supports registration, vehicle and policy registration, shift logging, trip assignment, start, completion, cancellation, fare details and feedback. It also supports operational queries and a small analytical snapshot. A front-end application is outside the deliverable.

The scenario is deliberately bounded. Vehicle ownership is fixed during the observation period; a driver may own several vehicles, but each vehicle has exactly one driver. A trip serves one passenger account. Shared rides, pooled passengers, driver substitutions and ownership history are excluded. These assumptions keep the original project manageable and make the functional dependencies explicit.

Fare records describe charges associated with completed trips. They are not payment confirmations, platform revenue or driver settlement statements. Payment gateways, recharge, refunds, real-time GPS, route optimization and regulatory eligibility verification are future extensions. No claim about legal driver eligibility follows from this teaching model.

The implementation uses MySQL, matching the SQL lectures. It contains 11 operational tables, two views, four lifecycle procedures, three guard triggers and an application role. Four additional tables form an analytical snapshot. All sample records are synthetic. The analysis illustrates what can be computed; it is not evidence about an actual ride-hailing business.''',
'''网约车平台需要把订单与乘客、实际服务车辆、负责司机以及最终结果对应起来。本项目围绕这些运营记录建立关系数据库，沿用原稿的用户角色、车辆、保险、轮班、行程和评价结构，同时统一主外键、状态规则及 SQL 实现。

主要参与者是乘客、司机和平台运营人员。数据库支持注册、车辆保险登记、轮班记录、下单、派单、开始、完成、取消、费用明细和双向评价，并支持运营查询和小型分析快照。本项目不包含前端应用。

业务范围采用明确假设：在观察期内，一辆车固定归属一名司机，一名司机可以有多辆车；一单对应一个乘客账号。不处理拼车、多乘客关联、换司机和车辆归属变更历史。这样能保持原稿规模，并清楚定义函数依赖。

行程费用只表示完成行程的收费记录，不等于已支付金额、平台收入或司机结算。支付网关、充值、退款、实时定位、路径优化及法规准入审核列为后续扩展。本教学模型不声称实现了法律合规判断。

实现采用与 SQL 课件一致的 MySQL，包含 11 张运营表、2 个视图、4 个生命周期过程、3 个保护触发器及应用角色；另有 4 张分析快照表。全部样例数据均为合成数据，分析结果只能用于演示数据库能力，不能推断真实网约车市场。''')
page('Requirements and acceptance criteria','需求与验收对应',
'''Each requirement is connected to a persistent object and an observable check. The database is judged by whether it represents the stated rules and rejects inconsistent changes, rather than by the number of entities alone. The course project specification requires the full development process and discussion; it does not prescribe a minimum table count.

A newly registered user may have no operational role yet. Passenger and driver roles can overlap. This supports a driver booking a ride as a passenger without duplicating their contact information. A booking exists before a vehicle is assigned, which makes optional participation necessary.

Insurance and shift records are stored for inspection and analysis. This version does not automatically reject assignment outside a shift or after insurance expiry. It also does not prevent two different trips being assigned simultaneously to one driver. Those are explicitly separate scheduling and dispatch constraints, not silently claimed features.''',
'''每项需求都对应一个数据对象和可观察的验收结果。评价设计时，应看它能否表达业务规则并拒绝不一致的变化，而不是单纯比较实体数量。项目说明要求完整开发过程和讨论，并没有规定最少表数。

刚注册的用户可以尚未拥有乘客或司机角色；这两种角色可以重叠，因此司机以乘客身份打车时不需要重复保存联系方式。下单发生在派车之前，所以行程到车辆的参与必须允许为空。

保险和轮班信息用于记录、检查和分析。本版不自动禁止在轮班之外或保险过期后派单，也不禁止同一司机同时被分配两个不同订单。这些属于尚未实现的调度约束，不能把存储相关记录理解为已经自动执行这些规则。''',
 table(['ID','Requirement / 需求','Objects and verification / 对象与验收'],[
 ['R1','Shared identity and overlapping roles','app_user, passenger, driver; one overlapping account'],
 ['R2','Vehicle and insurance records','vehicle, insurance_policy; immutable owner and date checks'],
 ['R3','Multiple shifts per day','driver_shift; composite key and chronological checks'],
 ['R4','Request and assign a vehicle','trip; request default, driver/vehicle match'],
 ['R5','Mutually exclusive terminal outcomes','completed_trip, cancelled_trip; procedures and guards'],
 ['R6','Fare components and two-sided feedback','surcharge, review; exact decimals and score checks'],
 ['R7','Operational and analytical queries','views and warehouse; counts, sums and query outputs'],
 ['R8','Reproducible implementation','seed, SQL, tests and saved machine-readable results']]))
page('Conceptual model','概念模型',
'''The model below shows all 11 entity types and their principal associations. Identity is separated from role-specific attributes. Trip is the business event; completion and cancellation store details that only exist for the corresponding outcome. The detailed cardinality table on the next page is authoritative where a compact diagram would otherwise obscure a rule.

DriverShift is identified by its driver and start time. It is an identification-dependent entity: its identity is only meaningful within a driver's shift history. InsurancePolicy has a globally unique policy identifier in this project, so it is a regular entity with an existence dependency on Vehicle, not a weak entity merely because it has a foreign key.''',
'''下图展示全部 11 种实体及主要联系。用户身份与角色专属属性分开保存；行程是核心业务事件；完成和取消详情只在对应结果发生后存在。下一页的基数表给出每条联系的完整规则，避免仅靠图上符号产生歧义。

轮班由司机和开始时间共同识别，身份依赖于司机，是可用于说明弱实体映射的例子。保险保单在本项目中有全局唯一编号，因此属于普通实体。虽然保单依赖车辆存在，但不能仅因为有外键就把它认定为弱实体。''',r'''
\begin{center}
\begin{tikzpicture}[x=1cm,y=1cm,box/.style={draw=accent,rounded corners=2pt,fill=accent!5,align=center,font=\small,text width=3cm,minimum height=1cm},every edge/.style={draw=accent},lab/.style={fill=white,font=\scriptsize,align=center}]
\node[box](u)at(0,0){AppUser\\user\_id};
\node[box](p)at(-4,-2){Passenger\\passenger\_id};
\node[box](d)at(4,-2){Driver\\driver\_id};
\node[box](t)at(-4,-5){Trip\\trip\_id};
\node[box](v)at(1,-4.5){Vehicle\\plate};
\node[box](h)at(5,-5){DriverShift\\driver\_id, shift\_start};
\node[box](i)at(1,-7){InsurancePolicy\\policy\_id};
\node[box](c)at(-5,-8.5){CompletedTrip\\trip\_id};
\node[box](x)at(-1,-8.5){CancelledTrip\\trip\_id};
\node[box](r)at(-6,-11){Review\\trip\_id};
\node[box](s)at(-2,-11){Surcharge\\trip\_id};
\draw (u)--node[lab,above left]{is a role}(p);
\draw (u)--node[lab,above right]{is a role}(d);
\draw (p)--node[lab,left]{requests\\1 : 0..N}(t);
\draw (d)--node[lab,above left]{owns\\1 : 0..N}(v);
\draw (d)--node[lab,right]{logs\\1 : 0..N}(h);
\draw (v)--node[lab,above]{serves\\0..1 : 0..N}(t);
\draw (v)--node[lab,right]{insured by\\1 : 0..N}(i);
\draw (t)--node[lab,left]{outcome\\1 : 0..1}(c);
\draw (t.south)--++(0,-.9)-|node[lab,pos=.8,left]{outcome\\1 : 0..1}(x.north);
\draw (c.south)--node[lab,left]{receives\\1 : 0..1}(r.north);
\draw (c.south)--node[lab,right]{has\\1 : 0..1}(s.north);
\end{tikzpicture}
\end{center}''')
rels=[['AppUser → Passenger','0..1','1','Partial overlapping specialization'],['AppUser → Driver','0..1','1','Same person can hold both roles'],['Driver → Vehicle','0..N','1','Owner fixed during observation'],['Vehicle → InsurancePolicy','0..N','1','Multiple policies/history allowed'],['Driver → DriverShift','0..N','1','Start time is a partial identifier'],['Passenger → Trip','0..N','1','One account requests each trip'],['Vehicle → Trip','0..N','0..1','Required after assignment'],['Trip → CompletedTrip','0..1','1','Only completed outcome'],['Trip → CancelledTrip','0..1','1','Only cancelled outcome'],['CompletedTrip → Review','0..1','1','One row may contain both scores'],['CompletedTrip → Surcharge','0..1','1','Absent row means zero surcharge']]
page('Relationships and business meaning','联系与业务含义',
'''Read the table as follows: for A → B, column two gives the number of B instances per A, and column three gives the number of A instances per B. A minimum of zero is optional participation; a minimum of one is mandatory participation. The outcome entities are additionally subject to the disjointness and state rules on the next page.

A driver-to-trip association is derivable through Vehicle. It is not stored a second time. For example, if DEMO001 belongs to driver 1, any trip assigned DEMO001 is served by driver 1 within the fixed-ownership assumption. A driver with DEMO001 and another vehicle can therefore be associated with many trips without losing which vehicle served each one.

The design contains several one-to-many and optional one-to-one associations. A many-to-many association is not added simply to demonstrate a notation. If the scope later permits driver/vehicle reassignment over time, an assignment-history entity will become necessary, and the current fixed-ownership dependency must be revised.''',
'''下表按 A → B 阅读：第二列表示一个 A 可以关联多少个 B；第三列表示一个 B 必须或可以关联多少个 A。下限为 0 表示可选参与，下限为 1 表示必选参与。完成与取消详情还必须满足下一页的互斥和状态规则。

司机与行程的联系可通过车辆推导，因此不重复保存。例如 DEMO001 在观察期内归属司机 1，则使用 DEMO001 的行程对应司机 1。司机拥有多辆车时，也能明确知道每单实际使用哪一辆。

设计自然包含一对多和可选一对一联系，没有为了展示某个符号强行加入多对多联系。如果后续允许司机和车辆随时间更换对应关系，就需要新增分配历史实体，并修改当前的固定归属假设。''',table(['A → B','B per A','A per B','Rule'],rels,'p{4.3cm}p{1.3cm}p{1.3cm}X'))
page('Specialization and trip lifecycle','特化规则与行程生命周期',
'''The AppUser specialization is partial and overlapping: an identity can have neither role, either role, or both. Passenger and Driver inherit user_id as both primary and foreign key. Shared contact attributes remain in AppUser.

Trip outcomes form a partial, disjoint specialization. An unfinished trip has no terminal detail. A COMPLETED trip has exactly one CompletedTrip and no CancelledTrip; a CANCELLED trip has exactly one CancelledTrip and no CompletedTrip. The implementation uses a status discriminator plus transaction-controlled detail creation.

Cancellation is allowed before a trip starts. Once IN_PROGRESS, this simplified lifecycle only permits completion; emergency termination and partial-service refunds are outside scope. REQUESTED requires no vehicle and no start time. ASSIGNED requires a vehicle but no start time. IN_PROGRESS and COMPLETED require both. CANCELLED may retain the previously assigned vehicle, but has no start time.''',
'''AppUser 的特化是部分且可重叠的：一个用户可以没有角色、只有一个角色，或同时拥有乘客和司机角色。两个子类都继承用户编号，并把它同时作为主键和外键，联系方式只保存在用户表。

行程结果是部分且互斥的特化。尚未结束的行程没有终态详情；完成状态必须恰好有一条完成详情且没有取消详情；取消状态反之。实现使用状态字段作为判别属性，通过事务把状态与详情一起写入。

本版只允许在开始前取消。进入 IN_PROGRESS 后只允许完成，紧急中止和部分服务退款不在范围内。待接单时车辆和开始时间为空；已派单时有车辆但没有开始时间；进行中和完成状态两者都有；取消状态可以保留先前分配车辆，但没有开始时间。''',r'''
\begin{center}\begin{tikzpicture}[node distance=1.7cm,>=Stealth,every node/.style={font=\small},state/.style={draw=accent,rounded corners,fill=accent!5,minimum width=3.1cm,minimum height=.8cm}]
\node[state](a){REQUESTED};\node[state,below=of a](b){ASSIGNED};\node[state,below=of b](c){IN\_PROGRESS};\node[state,below=of c](d){COMPLETED};\node[state,right=3cm of b](x){CANCELLED};
\draw[->](a)--node[right]{assign\_trip}(b);\draw[->](b)--node[right]{start\_trip}(c);\draw[->](c)--node[right]{complete\_trip}(d);\draw[->](a.east)-|node[above,pos=.3]{cancel\_trip}(x.north);\draw[->](b)--node[above]{cancel\_trip}(x);
\end{tikzpicture}\end{center}
\begin{equation*}
\begin{gathered}{}[status=COMPLETED]\iff[\exists!\ CompletedTrip],\\
[status=CANCELLED]\iff[\exists!\ CancelledTrip].\end{gathered}
\end{equation*}''')
page('Mapping the model into relations','从概念模型到关系模式',
'''Regular entities map to tables with their identifiers as primary keys. A one-to-many association puts the parent's key on the many side: passenger_id is stored in Trip, and plate is stored in InsurancePolicy. An optional association uses a nullable foreign key, as in an unassigned Trip.

Each role subtype gets a table whose primary key also references AppUser. Each outcome subtype likewise shares Trip's key. Review and Surcharge use the completed trip identifier as their own primary key: this enforces at most one row of each kind per completed trip without an unnecessary independent identifier.

DriverShift maps to the composite key (driver_id, shift_start). A separate calendar-date key is not sufficient because a driver can work twice on the same day. Dates needed for grouping are derived from timestamps. InsurancePolicy uses a unique policy_id rather than a redundant composite key containing both policy and vehicle.

The original draft stored both driver and vehicle-related information around Trip. Under fixed ownership, plate determines driver_id. Storing both in Trip would introduce a non-key determinant and an update anomaly. Trip therefore stores plate only, while trip_service exposes the derived driver identifier for convenient queries. The dispatch interface still accepts both driver and plate and checks that they match.''',
'''普通实体转换为以标识符为主键的表。一对多联系把“一端”的键放到“多端”，例如 Trip 保存 passenger_id，InsurancePolicy 保存 plate。可选联系使用可空外键，例如未派单行程的车辆。

角色子类各自建表，主键同时引用 AppUser。行程结果子类同样共享 Trip 的主键。Review 和 Surcharge 使用完成行程编号作为主键，因此每单最多一条相应记录，不需要再引入无用的独立编号。

DriverShift 使用 (driver_id, shift_start) 复合主键。只用日期无法区分同一天的多次轮班；需要按天统计时从时间戳推导日期。保单使用唯一 policy_id，不再使用同时包含保单号和车牌的冗余复合键。

在车辆固定归属的假设下，plate 决定 driver_id。如果把两者同时放在 Trip，会出现非键决定因素和更新异常。因此 Trip 只存 plate，通过 trip_service 视图提供派生的司机编号。派单接口仍接收司机和车牌，并验证两者一致。''',table(['Relation','Primary key','Foreign key targets'],[
['app_user','user_id','—'],['passenger','passenger_id','app_user'],['driver','driver_id','app_user'],['vehicle','plate','driver'],['insurance_policy','policy_id','vehicle'],['driver_shift','driver_id, shift_start','driver'],['trip','trip_id','passenger, vehicle'],['completed_trip','trip_id','trip'],['cancelled_trip','trip_id','trip'],['review','trip_id','completed_trip'],['surcharge','trip_id','completed_trip']]))
meta=list(csv.DictReader((R/'results/data_dictionary.tsv').read_text().splitlines(),delimiter='\t'))
meaning={'app_user':'用户','passenger':'乘客','driver':'司机','vehicle':'车辆','insurance_policy':'保险','driver_shift':'轮班','trip':'行程','completed_trip':'完成行程','cancelled_trip':'取消行程','review':'评价','surcharge':'附加费'}
for group,title,zt in [(['app_user','passenger','driver'],'Data dictionary for identities','身份数据字典'),(['vehicle','insurance_policy','driver_shift'],'Data dictionary for vehicles and shifts','车辆与轮班数据字典'),(['trip'],'Data dictionary for bookings','行程主表数据字典'),(['completed_trip','cancelled_trip','review','surcharge'],'Data dictionary for outcomes','行程结果数据字典')]:
 extra=''
 for t in group:
  extra+='\\subsection*{'+esc(t+' / '+meaning[t])+'}\n'
  extra+=table(['Column','SQL type','Null','Key'],[[x['COLUMN_NAME'],x['COLUMN_TYPE'],x['IS_NULLABLE'],x['COLUMN_KEY'] or '—'] for x in meta if x['TABLE_NAME']==t],'p{4.4cm}p{4.0cm}p{1.5cm}X')
 page(title,zt,'''The definitions below are extracted from the running database's information_schema, so they describe the executed schema rather than an independently maintained design. PRI denotes a primary-key component; UNI denotes a unique index; MUL denotes an indexed non-unique column and is not itself proof of a foreign key. Foreign-key targets are listed in the mapping section.

All identifiers are supplied explicitly by the data loader; no vendor-specific automatic identity generator is needed. Empty optional values use SQL NULL. Phone numbers are text, and monetary values use DECIMAL to avoid floating-point rounding in financial aggregation.''',
 '''下列定义直接提取自运行数据库的 information_schema，反映实际执行的结构。PRI 表示主键组成部分，UNI 表示唯一索引，MUL 表示非唯一索引列，本身不能证明该列有外键；外键引用对象见关系映射部分。

所有编号由数据加载程序明确提供，不依赖自动编号语法。缺失的可选值使用 SQL NULL；电话号码使用文本类型；金额使用 DECIMAL，避免浮点误差影响费用汇总。''',extra)
fdrows=[['app_user','user_id; phone','Either key → all other attributes'],['passenger','passenger_id','passenger_id → tier'],['driver','driver_id; license_no','Either key → all other attributes'],['vehicle','plate','plate → driver_id, model, color, capacity'],['insurance_policy','policy_id','policy_id → plate, valid_from, valid_to'],['driver_shift','(driver_id, shift_start)','Composite key → shift_end'],['trip','trip_id','trip_id → every remaining attribute'],['completed_trip','trip_id','trip_id → ended_at, base_fare, tip, actual_km'],['cancelled_trip','trip_id','trip_id → cancelled_at, reason'],['review','trip_id','trip_id → both scores and comments'],['surcharge','trip_id','trip_id → amount']]
page('Functional dependencies and normal forms','函数依赖与范式',
'''Normalization is evaluated against the declared business rules, not accidental patterns in 200 sample records. In the dependencies below, each candidate key determines all remaining attributes of its relation. Phone and license_no are mandatory and unique, so they are alternate candidate keys. Email is neither mandatory nor unique and is not a candidate key.

Attributes are scalar within the chosen domains, satisfying 1NF. DriverShift is the only operational table with a composite primary key. Its end time depends on the full pair: the driver alone has many shifts and the start time alone may be shared by different drivers. Thus no proper subset determines shift_end, satisfying 2NF.

No additional non-trivial dependency with a non-key determinant is assumed within any operational table. In particular, vehicle model is a descriptive category, not a unique vehicle specification; capacity is measured per registered vehicle. Fare is not determined solely by distance. Under these stated dependencies, the 11 tables satisfy BCNF and hence 3NF. This is a conditional design argument, not a claim that finite sample data can prove all business dependencies.''',
'''规范化依据已声明的业务规则，而不是 200 条样例数据中的偶然规律。下表中的每个候选键都决定该关系的所有其余属性。phone 和 license_no 均要求非空且唯一，因此是备用候选键；email 不满足这些条件，不能作为候选键。

所有属性在选定的值域内都是单值，满足 1NF。DriverShift 是唯一有复合主键的运营表。结束时间依赖完整的“司机、开始时间”组合：一个司机有多个班次，不同司机也可以同时开始，因此不能只依赖其中一部分，满足 2NF。

在本项目假设中，各运营表内部没有其他以非候选键为决定因素的非平凡依赖。车辆型号是描述性类别，不是唯一规格编码；容量按具体车辆登记；费用也不只由距离决定。因此，在这些依赖成立的条件下，11 张表满足 BCNF，进而满足 3NF。这是基于业务规则的论证，不能用有限样例数据证明所有依赖。''',table(['Relation','Candidate keys','Functional dependencies'],fdrows,'p{3.0cm}p{4.0cm}X'))
page('Normalization decisions and anomalies','规范化决策与异常分析',
'''Consider a hypothetical Trip(trip_id, plate, driver_id, ...). Since trip_id identifies the trip and plate identifies its fixed owner, trip_id → plate → driver_id. Plate is not a candidate key of Trip because the same vehicle serves many trips. Keeping driver_id there violates 3NF and BCNF under the fixed-ownership rule. The implemented decomposition keeps ownership in Vehicle and only plate in Trip. Joining on plate recovers the assigned driver; unassigned trips require a LEFT JOIN to preserve them.

User contact information is also stored once. Duplicating phone and address across Passenger and Driver would require coordinated updates for overlapping roles. Shared primary-key foreign keys retain a single identity while allowing role-specific attributes.

Surcharge is separated because it is an optional detail and the original framework already used this entity. If amount were stored directly in CompletedTrip, with trip_id still its only determinant, that relation could still satisfy BCNF. Optionality and convenience are not proofs of a normalization violation. Likewise, subtype tables express semantic differences, not an automatic improvement in normal form.

The outcome decomposition shares a key with Trip and avoids repeating booking attributes. Foreign keys guarantee that a detail has a parent, while primary keys guarantee at most one detail. They do not alone guarantee that every completed status has its detail or that the two outcomes are mutually exclusive. Those constraints require the lifecycle implementation and privilege boundary described next.

Historical vehicle reassignment would invalidate plate → fixed driver over the full history. A future design must introduce a temporally identified assignment and link each trip to that assignment. Updating vehicle.driver_id in place would incorrectly change the apparent driver of past trips, so the current implementation rejects that update.''',
'''假设保留 Trip(trip_id, plate, driver_id, ...)，那么 trip_id 决定 plate，而固定车辆归属又使 plate 决定 driver_id。一辆车服务多单，所以 plate 不是 Trip 的候选键；这种传递依赖违反 3NF 和 BCNF。实现把归属关系保留在 Vehicle，Trip 只保存 plate，通过连接恢复司机。对于未派车订单，需要 LEFT JOIN 才不会丢失记录。

用户联系方式也只保存一次。如果 Passenger 和 Driver 都保存电话和地址，具有双角色的用户修改联系方式时就必须协调更新。共享主键外键既保留身份一致性，也允许各角色拥有自己的属性。

Surcharge 单独建表是因为它属于可选详情，且原稿已经采用该结构。如果直接把附加费放进 CompletedTrip，而唯一决定因素仍是 trip_id，该表仍可能满足 BCNF。因此，“有时没有附加费”和“拆表更方便”都不是违反范式的证明。子类拆表同样是表达语义，而不是自动提高范式。

结果子表共享 Trip 的键，不重复下单属性。外键保证子记录有父记录，主键保证最多一条，但它们不能单独保证完成状态一定有完成详情，也不能单独保证两个结果互斥。这需要生命周期实现和权限边界共同保证。

如果以后允许车辆换司机，整个历史上的 plate → 固定司机假设就不再成立。届时应增加带时间标识的分配记录，并把行程指向该记录。直接更新车辆司机会错误改变历史行程的司机，因此当前触发器拒绝这种修改。''')
page('SQL implementation and integrity','SQL 实现与完整性',
'''The executed engine is MySQL '''+D['version'][0]['version']+'''. All operational tables use InnoDB. PRIMARY KEY and UNIQUE constraints protect entity identity; FOREIGN KEY constraints protect references; CHECK constraints enforce local domains and chronology. Referenced history is protected by the default restrictive deletion policy. There is no broad ON DELETE CASCADE from a user to completed service records.

The application role can create identities and registration records, insert only the permitted booking columns, submit or update reviews, read results, and execute lifecycle procedures. It cannot directly change Trip.status or insert/update outcome records. Procedure execution uses the definer's privileges. The disposable test account is removed after verification; the delivery does not ship a passwordless production account.

Guard triggers validate a completion's parent state and end time, validate a cancellation's parent state and time, and prevent vehicle-owner changes. Because ordinary MySQL CHECK expressions cannot express all cross-table invariants here, the lifecycle procedures enforce the complete state/detail change as one transaction. An administrator with direct write access can still bypass the intended workflow; the report's guarantee applies to the application interface and declared role.

Indexes include (passenger_id, requested_at) for passenger history and (status, requested_at) for operational filtering. Primary and foreign-key indexes support joins. The saved EXPLAIN output documents the optimizer's actual choice on this small dataset; no production latency claim is made. In this run, the passenger-history query uses range access on ix_trip_passenger_time with an estimate of 3 rows and Using index condition.''',
'''实际执行引擎为 MySQL '''+D['version'][0]['version']+'''，所有运营表使用 InnoDB。主键和唯一约束保护实体标识，外键保护引用，CHECK 检查本行的值域和时间顺序。删除引用对象时采用默认限制策略，不从用户向历史行程进行大范围级联删除。

应用角色可以创建身份和登记记录，只能插入允许的下单字段，可以提交或修改评价、读取结果，并调用生命周期过程。它不能直接修改 Trip.status，也不能直接写入结果子表。过程通过定义者权限完成受控操作。测试用临时账号在验证后删除，交付不提供无密码生产账号。

保护触发器检查完成记录的父状态和结束时间、取消记录的父状态和取消时间，并禁止车辆归属变更。跨表一致性不能全部依靠本行 CHECK，因此通过事务过程把状态和详情作为一个整体写入。拥有直接写权限的管理员仍可能绕过流程；一致性保证针对声明的应用接口和角色。

索引包括用于乘客历史查询的 (passenger_id, requested_at) 和用于运营筛选的 (status, requested_at)。主外键索引支持连接。保存的 EXPLAIN 反映小样本上的实际优化器选择，不据此声称达到生产性能。本次乘客历史查询实际使用 ix_trip_passenger_time 的 range 访问，估计扫描 3 行，Extra 为 Using index condition。''',code('''CREATE VIEW trip_service AS
SELECT t.*, v.driver_id
FROM trip t LEFT JOIN vehicle v ON v.plate=t.plate;

-- A booking cannot directly choose status or completion detail
-- when inserted through the application role.
GRANT INSERT (trip_id, passenger_id, requested_at,
 origin_zone, destination_zone, service_type,
 estimated_km, estimated_fare)
ON ride_hailing.trip TO 'ride_hailing_app';'''))
page('Transactions and concurrent requests','事务与并发请求',
'''Each lifecycle procedure starts a transaction, reads the target Trip row with SELECT ... FOR UPDATE, checks its current state, performs the required writes, then commits. An exception handler rolls back and rethrows the error. Procedures own their transaction boundary and must be called without an already active caller transaction: MySQL does not provide nested transactions here.

Assignment verifies that the supplied driver owns the supplied vehicle. Start checks the ASSIGNED state; the local CHECK rejects a start before the request. Completion inserts CompletedTrip, validates and optionally inserts Surcharge, then changes the status. Cancellation inserts its detail and updates the status. The row lock serializes two competing lifecycle operations for the same trip.

The rollback test deliberately supplies a negative surcharge after a completion detail has been inserted. The raised error must undo that insert and leave the parent IN_PROGRESS. This checks atomicity across multiple writes rather than merely checking that invalid input is rejected early.

The concurrent test opens two independent client connections and asks both to complete the same active trip. Exactly one succeeds; the other observes the terminal state after acquiring the lock and is rejected. This demonstrates same-trip serialization. It does not test multi-driver dispatch optimization, distributed failures, throughput, or driver-level double-booking prevention.''',
'''每个生命周期过程先开始事务，用 SELECT ... FOR UPDATE 锁定目标行程，检查当前状态，执行必要写入，然后提交。异常处理器回滚并重新抛出错误。过程负责自己的事务边界，因此调用方不能在已开启的事务中调用；这里没有嵌套事务语义。

派单验证指定司机是否拥有指定车辆。开始过程要求状态为 ASSIGNED，并由 CHECK 拒绝早于下单的开始时间。完成过程先写入完成详情，再验证和写入可选附加费，最后改变主表状态。取消过程同样写详情并更新状态。行锁使同一行程的竞争操作依次执行。

回滚测试故意让完成详情先插入，再提交负附加费触发异常。正确结果应撤销前面的详情插入，且父行程仍为 IN_PROGRESS。这验证了多步写入的原子性，而不只是入口处拒绝非法输入。

并发测试使用两个独立客户端同时完成同一进行中订单。应恰好一个成功，另一个获得锁后发现终态并被拒绝。这验证同一订单的串行化，不等于测试了多司机调度、分布式故障、吞吐量或司机重复派单预防。''',code('''START TRANSACTION;
SELECT status INTO v_status
FROM trip WHERE trip_id=p_trip FOR UPDATE;
-- Require IN_PROGRESS, otherwise SIGNAL SQLSTATE '45000'.
INSERT INTO completed_trip VALUES
 (p_trip,p_end,p_base,p_tip,p_km);
-- Invalid surcharge raises an error here; handler rolls back.
IF p_extra > 0 THEN
 INSERT INTO surcharge VALUES(p_trip,p_extra);
END IF;
UPDATE trip SET status='COMPLETED' WHERE trip_id=p_trip;
COMMIT;'''))
page('Synthetic dataset and reproducibility','合成数据与可复现性',
'''The generator uses a local pseudorandom seed of 20261118. It creates 200 trips requested from 1 to 20 October 2026, with a predetermined mix of terminal and open states shuffled across the period. Timestamps are local Asia/Shanghai civil times stored as DATETIME; timezone conversion is not part of this single-region example.

The data includes one identity with both roles, one registered identity with neither role, multiple vehicles for selected drivers, and two shifts per driver per day. Completed trips include optional tips, optional surcharges and partial or bilateral feedback. Cancellation can occur before or after assignment. Open states intentionally exercise optional relationships.

All personal names, contact values, license numbers and vehicle identifiers are fabricated. The email domain example.invalid prevents them from resembling usable addresses. The generated state proportions and fees are input assumptions, not measured business performance. Stored driver lifetime_km is a registration snapshot, not an aggregate maintained from these trips.

The reproduction sequence creates a new schema, loads routines, generates and imports synthetic records through the lifecycle interface, builds the analytical snapshot, creates the application role, then runs validation. Test fixtures use reserved identifiers and are removed before published outputs are collected. The generator seed and resulting counts are retained alongside the SQL and query results.''',
'''生成器使用固定随机种子 20261118，生成 2026 年 10 月 1 日至 20 日期间请求的 200 条行程。各状态数量预先设定，再打乱分布到整个期间。时间使用上海本地民用时间，以 DATETIME 保存，本单地区示例不处理时区转换。

数据包含一个双角色用户、一个尚无角色的注册用户、部分司机拥有多辆车，以及每位司机每天两次轮班。完成行程覆盖可选打赏、附加费、单边和双边评价。取消可以发生在派单前或派单后；开放状态用于验证可选关联。

姓名、联系方式、驾驶证和车牌均为虚构，邮箱使用 example.invalid。状态比例和费用来自生成规则，不是实测业务表现。司机 lifetime_km 是登记快照，不由本批行程自动累加。

复现流程依次创建新 schema、加载过程、生成并通过生命周期接口导入数据、建立分析快照、创建应用角色和运行验证。测试使用保留编号，发布查询结果前清除这些临时记录。随机种子、实际行数、SQL 及查询输出一并保留。''',result('counts',['table_name','rows_n'],['Operational table','Rows']))
page('Validation results','验证结果',
'''All '''+str(len(V))+''' recorded checks passed on the executed database. Negative tests require a specific MySQL error category rather than accepting any failure. Checks cover identity and reference integrity, local domains, chronological order, workflow rules, rollback, concurrent completion, restricted application access and analytical reconciliation.

Successful insertion, update and deletion are exercised on disposable records. Attempts to delete a referenced user are rejected. The privilege test confirms that the application cannot directly update Trip.status, while an authorized request followed by cancellation succeeds.

The table below groups the checks for readability. Full test names, pass flags and captured error messages are supplied in validation.json. These checks provide evidence for the stated workflow and dataset; they do not establish production readiness, crash recovery behavior or exhaustive security testing.''',
'''本次数据库运行记录的 '''+str(len(V))+''' 项检查全部通过。负向测试要求出现指定 MySQL 错误类别，不会把任意失败都当成通过。覆盖身份与引用完整性、值域、时间顺序、流程规则、回滚、并发完成、应用权限及分析层核对。

成功的插入、修改和删除使用临时记录演示；删除被引用用户的尝试被拒绝。权限测试确认应用角色不能直接更新行程状态，但允许下单并调用取消过程。

下表按类型汇总，完整测试名称、通过标记及错误消息保存在 validation.json。这些检查为声明的流程和样例数据提供证据，不代表生产就绪，也没有完成崩溃恢复或穷尽安全测试。''',table(['Area','Observed checks','Outcome'],[
['Keys and references','Duplicate ID, duplicate review, missing parent, protected deletion','Pass'],['Domains','Out-of-range score, empty feedback, negative amount, required name','Pass'],['Time','Shift end, start before request, completion before start','Pass'],['Workflow','Owner immutability, wrong driver, disjoint outcomes, terminal state','Pass'],['Transactions','Partial write undone; parent state retained; success path','Pass'],['Concurrency','Two completions: exactly one commit','Pass'],['Privileges','Direct status write denied; authorized request/cancel allowed','Pass'],['Reconciliation','200 trips, state/detail alignment, no fanout, warehouse count/fare','Pass'],['Coverage','Overlapping role, two shifts per day, CRUD cleanup','Pass']]))
page('Operational SQL and query semantics','运营查询与统计口径',
'''The financial view joins each completed trip to at most one surcharge. COALESCE converts the missing optional row into zero; it does not hide missing completion records. Total fare is base_fare + tip + surcharge. This explicitly avoids adding a surcharge twice if a field called actual fare were already defined as an inclusive total.

Driver summaries start from Driver and LEFT JOIN completed trips so that drivers with no completed trips would remain visible. COUNT(f.trip_id), not COUNT(*), counts actual matches. Passenger rating averages ignore SQL NULL, and the scored count is reported alongside the average. A driver with no ratings has an unknown mean, not a zero-quality score.

The insurance query uses a fixed analysis date of 1 November 2026 and includes policies expiring between that date and 30 days later. Fixing the reference date makes reruns stable. It lists policy records, not necessarily vehicles without replacement coverage; determining coverage gaps would require considering all policies for each vehicle.''',
'''费用视图把每条完成行程与至多一条附加费连接。COALESCE 把不存在的可选附加费视作 0，不会掩盖缺失的完成详情。总费用明确等于基础费用、打赏和附加费之和，避免把已经包含附加费的“实际费用”再重复相加。

司机汇总从 Driver 出发，LEFT JOIN 完成行程，以保留没有完成订单的司机。COUNT(f.trip_id) 统计实际匹配数，而不是 COUNT(*)。乘客评分平均值忽略 SQL NULL，同时报告有效评分数。没有评分意味着未知，不等于服务质量为零。

保险查询固定使用 2026 年 11 月 1 日作为参考日，包含从当天到 30 天后到期的保单，保证复现稳定。结果是保单清单，并不一定代表车辆未来没有有效续保；判断保障缺口需要综合同一车辆的所有保单。''',code('''SELECT d.driver_id, COUNT(f.trip_id) AS completed,
       COALESCE(SUM(f.total_fare),0) AS gross_fare,
       ROUND(AVG(r.passenger_score),2) AS mean_score,
       COUNT(r.passenger_score) AS scored
FROM driver d
LEFT JOIN trip_financials f ON f.driver_id=d.driver_id
LEFT JOIN review r ON r.trip_id=f.trip_id
GROUP BY d.driver_id ORDER BY gross_fare DESC;

SELECT policy_id,plate,valid_to FROM insurance_policy
WHERE valid_to BETWEEN '2026-11-01'
 AND DATE_ADD('2026-11-01',INTERVAL 30 DAY);''')+result('insurance',['policy_id','plate','valid_to']))
f=D['finance'][0]
page('Observed results and interpretation','实际查询结果与解释',
'''The request-cohort completion share is 130/200 = 65%; the cancellation share is 30/200 = 15%. Forty requests remain in open states. Among terminal trips only, completion is 130/160 = 81.25%. These denominators answer different questions and must not be interchanged. In an actual longitudinal study, cohorts would need a common observation cutoff and sufficient follow-up.

Completed trips have a total fare of '''+f['total_fare']+''' currency units and a mean fare of '''+f['mean_fare']+'''. The mean inclusive fare minus estimated fare is '''+f['mean_difference']+'''. This difference includes tips and surcharges and therefore is not a pure estimation-error metric. Total surcharges are '''+f['surcharges']+''' and tips are '''+f['tips']+'''. No platform commission is modeled, so gross fare should not be labelled platform revenue.

Driver 3 has the largest completed-trip fare total in this generated sample. Drivers 4 and 8 have no passenger scores because the deterministic review selection aligns with their generated trip identifiers. That missingness is a generator artifact, not evidence about their service. Comparisons would require representative samples and exposure measures; identical scheduled shifts do not demonstrate equal actual working time.''',
'''按全部请求计算，完成占比为 130/200 = 65%，取消占比为 30/200 = 15%，还有 40 条处于开放状态。如果只统计已结束订单，完成占比为 130/160 = 81.25%。两种分母回答不同问题，不能混用。真实纵向分析应统一观察截止点并留出充分跟踪时间。

完成行程总费用为 '''+f['total_fare']+''' 个货币单位，平均费用为 '''+f['mean_fare']+'''。包含所有费用后的实际总额减预估费用，平均差额为 '''+f['mean_difference']+'''；差额包含打赏和附加费，不能直接当作纯粹的估价误差。附加费合计 '''+f['surcharges']+'''，打赏合计 '''+f['tips']+'''。模型没有平台抽成，因此不能把总收费称为平台收入。

合成样本中，司机 3 的完成行程收费总额最高。司机 4 和 8 没有乘客评分，是因为确定性评价选择规则与其行程编号分配重合。这是生成器带来的缺失模式，不代表真实服务表现。公平比较还需要代表性数据和服务暴露量；安排相同轮班并不能证明实际工作时长相等。''',result('status',['status','trips','percent_all'],['State','Trips','% of all requests'])+'\\vspace{5mm}\n'+result('drivers',['driver_id','completed','gross_fare','mean_score','scored'],['Driver','Completed','Gross fare','Mean score','Scored']))
page('Analytical star schema','分析星型模型',
'''Lecture 10 distinguishes transaction processing from analytical workloads. The operational schema prioritizes normalized updates and integrity. A separate snapshot provides a simpler structure for repeated aggregation. Its fact grain is exactly one completed trip, identified by trip_id. Cancelled and open trips are intentionally absent; this fact table cannot be used by itself to compute request cancellation rates.

The fact table stores additive total_fare and actual_km, plus estimated_fare, and references date, driver and vehicle dimensions. The date key is the completion date, not the request date. Duration and averages are computed at query time. Date attributes are intentionally redundant for analytical convenience; the OLTP normalization argument is not applied unchanged to the star schema.

The implementation is a single full-load snapshot after the operational seed finishes. It is not an incremental ETL service and has no slowly changing dimension history. Driver and vehicle dimensions reflect the observation-period snapshot. A production design would define refresh boundaries, late-arriving changes, historical dimensions and validation before publication.''',
'''Lecture 10 区分事务处理与分析工作负载。运营库优先考虑规范化更新和一致性；独立快照为重复汇总提供更简单的结构。事实表粒度是一条完成行程，以 trip_id 标识。取消和开放行程不进入此表，因此不能只靠它计算全部请求的取消率。

事实表保存可加总的总费用、实际里程和预估费用，并关联日期、司机、车辆维度。日期键使用完成日期，而非请求日期。平均数等指标在查询时计算。日期维度为分析便利保留冗余属性，因此不能把运营库的范式论证原封不动套在星型模型上。

实现是在种子数据导入后执行一次完整快照加载，没有增量 ETL 服务，也没有缓慢变化维度历史。司机和车辆维度反映观察期快照。生产系统还需要定义刷新边界、迟到数据、历史维度和发布前核验。''',r'''
\begin{center}\begin{tikzpicture}[>=Stealth,box/.style={draw=accent,fill=accent!5,rounded corners,align=center,text width=4cm,minimum height=1.3cm,font=\small}]
\node[box](f)at(0,0){dw\_trip\_fact\\PK trip\_id\\date, driver, vehicle keys\\total\_fare, actual\_km, estimated\_fare};
\node[box](d)at(0,3.5){dw\_date\\PK date\_key\\year, month, day};
\node[box](r)at(-4,-3.5){dw\_driver\\PK driver\_key\\driver\_name};
\node[box](v)at(4,-3.5){dw\_vehicle\\PK vehicle\_key\\model, capacity};
\draw[->](f)--node[right,font=\small]{N : 1}(d);\draw[->](f)--node[left,font=\small]{N : 1}(r);\draw[->](f)--node[right,font=\small]{N : 1}(v);
\end{tikzpicture}\end{center}''')
page('OLAP queries and reconciliation','OLAP 查询与数据核对',
'''The executed ROLLUP query groups by completion year, month and vehicle model. It yields model details, monthly subtotals, annual subtotals and a grand total. In this one-month dataset the last three totals happen to match. NULL in those output grouping columns denotes a subtotal level, not a missing dimension value. The dimension source columns are non-null.

The analytical fact has 130 rows, equal to CompletedTrip. Its total fare is '''+f['total_fare']+''', exactly matching trip_financials. Each trip identifier is unique, and optional surcharge and review joins are checked not to multiply fact rows. These reconciliations guard against a common analytical error: an apparently plausible sum inflated by a one-to-many join.

Additional delivered queries use LAG to compare adjacent observed completion days and a scalar subquery with HAVING to select drivers whose mean fare exceeds the overall completed-trip mean. LAG means the previous observed date; if a day is absent, it is not automatically the previous calendar day. The complete query output is saved in TSV and JSON files.''',
'''实际执行的 ROLLUP 按完成年份、月份、车型分组，产生车型明细、月小计、年小计和总计。本数据只覆盖一个月，因此后三层总额恰好相同。分组输出中的 NULL 表示汇总层级，并非维度值缺失；维度来源字段本身不为空。

分析事实表有 130 行，与 CompletedTrip 一致，总费用为 '''+f['total_fare']+'''，与 trip_financials 完全相符。行程编号唯一，并检查可选附加费及评价连接不会放大行数。这类核对能发现一对多连接把金额重复累计的问题。

配套查询还使用 LAG 比较相邻有观测记录日期的费用，并用标量子查询与 HAVING 筛选平均费用高于整体平均的司机。LAG 表示前一个有记录的日期；如果某天没有记录，不能自动理解为前一个自然日。全部结果保存在 TSV 和 JSON 中。''',code('''SELECT d.calendar_year,d.calendar_month,v.model,
 COUNT(*) AS trips,SUM(f.total_fare) AS gross_fare
FROM dw_trip_fact f
JOIN dw_date d ON d.date_key=f.date_key
JOIN dw_vehicle v ON v.vehicle_key=f.vehicle_key
GROUP BY d.calendar_year,d.calendar_month,v.model WITH ROLLUP;''')+result('rollup',['calendar_year','calendar_month','model','trips','gross_fare'],['Year','Month','Model','Trips','Fare']))
page('Discussion and design limitations','讨论与设计边界',
'''The strongest improvement over the starting design is consistency across requirements, diagrams, relational keys and executable behavior. A booking can now exist before assignment, each served trip identifies a vehicle, terminal outcomes are distinguished from all unfinished trips, and normalization claims are tied to explicit dependencies.

The fixed vehicle-owner rule is a deliberate simplification that supports a small, coherent schema. It should not be generalized to a platform where vehicles are shared among drivers over time. A temporal assignment model would be the first structural extension in that setting. Similarly, one bilateral review row is convenient for one passenger and one driver per trip; repeated reviews, moderation and revision history would require additional structure.

The application role protects workflow integrity, but it is a service-level role, not per-customer authorization. An application must still verify that an authenticated person is allowed to review a particular trip or read personal information. Authentication, row-level access, encryption policy, retention and production monitoring are outside this database demonstration.

Shift overlaps, driver availability across trips, active insurance at dispatch and customer cancellation fees are not automatically enforced. The stored records make some related queries possible, but data storage should not be mistaken for a completed policy engine. Financial records also do not prove money was paid or settled.

The dataset is small, generated and deliberately covers edge cases. Execution plans are informative about chosen access paths, not benchmarks. The tested concurrency case is limited to two simultaneous completions of one trip. A deployable system would need load testing, failure recovery, operational access controls, richer state transitions and representative data.

Within these limits, the project completes the required path from business requirements through conceptual and logical design to executable implementation and data-use discussion. The analytical extension illustrates the different goals of OLTP and OLAP without replacing the operational model.''',
'''相对于起始文档，核心改进在于需求、图、关系键和实际行为彼此一致：下单可以早于派车；每个已服务订单能识别实际车辆；终态详情与所有未完成行程明确区分；范式结论有明确依赖依据。

车辆固定归属是控制规模的有意简化，不能推广到司机随时间共享车辆的平台。若需要该场景，应优先引入带时间的分配历史。每单一条双向评价记录适用于一名乘客和一名司机；多次评价、审核和修改历史需要额外结构。

应用角色保护数据库流程完整性，但它是服务级角色，不是按具体客户隔离的数据权限。应用仍需确认登录者是否有权评价某单或查看个人信息。身份认证、逐行访问、加密策略、保留期限和生产监控不属于本数据库演示。

轮班重叠、跨订单司机可用性、派单时保险有效性及取消费用没有自动执行。虽然已存储的数据支持部分检查查询，但不能把保存记录理解为已完成业务规则引擎。费用记录也不证明资金实际支付或结算。

样本小、由程序生成并刻意覆盖边界情况。执行计划只能说明所选访问路径，不能充当性能基准。并发测试仅覆盖两个请求完成同一订单。部署前还需要负载测试、故障恢复、运行权限、更完整的状态变化及代表性数据。

在这些边界内，项目完成了从业务需求、概念和逻辑设计到可执行实现和数据用途讨论的完整过程。分析扩展用于展示 OLTP 与 OLAP 的不同目标，而不替代运营模型。''')
page('Course alignment and references','课程对应与参考材料',
'''The project requirement asks for context and requirements, ER/EER design, relational design, implementation, and discussion of database construction and data usage. The report's sections follow that sequence. The following mapping identifies how the available lectures inform the work. Lecture 1 was not present among the supplied files; no specific requirement is attributed to an unseen lecture.

The original ride-hailing document is the starting design. Terminology referring to an online shopping mall has been removed. No additional mandatory entity count, UI implementation, or warehouse delivery requirement is inferred from classroom examples; the warehouse is a bounded analytical extension.''',
'''项目说明要求背景和需求、ER/EER 设计、关系设计、数据库实现，以及建库与数据使用讨论。本报告按此流程展开。下表说明已有课件与报告的对应关系。所提供文件中没有 Lecture 1，因此不把未见材料中的内容当作具体要求。

原网约车文档是起始设计。已删除误写的网上商城术语。不把课堂例子推断为额外的实体数量、界面实现或数据仓库必交要求；仓库是范围明确的分析扩展。''',table(['Source','Applied concepts'],[
['Group Project Requirements, Fall 2026','Five development components and depth/reliability criteria'],['LN2 Relational data model','Domains, keys, integrity and business context'],['LN3 Conceptual model and ER diagrams I','Entities, attributes, cardinality, weak entities'],['LN4 Conceptual model and ER diagrams II','Partial/total and overlapping/disjoint specialization'],['LN5 Logical design and theory I','Entity/relationship/subtype mapping to relations'],['LN6 Logical design and theory II','Functional dependencies, 1NF, 2NF, 3NF and BCNF'],['LN7 SQL basic','MySQL DDL, constraints and CRUD'],['LN8 SQL basic','NULL, joins, aggregation, filtering and subqueries'],['LN9 Advanced SQL','Views, advanced queries and transactions'],['LN10 Data Warehouse','OLTP/OLAP, star schema, ROLLUP and LAG']])+
 r'''\subsection*{Implementation references}
\begin{itemize}\small
\item MySQL 8.4 Reference Manual, \emph{CHECK Constraints}: \url{https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html}.
\item MySQL 8.4 Reference Manual, \emph{Locking Reads}: \url{https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html}.
\item MySQL 8.4 Reference Manual, \emph{GROUP BY Modifiers}: \url{https://dev.mysql.com/doc/refman/8.4/en/group-by-modifiers.html}.
\end{itemize}''')
page('Reproduction and evidence inventory','复现步骤与证据文件',
'''Use a disposable MySQL 8.4 instance with an empty schema namespace. The schema script intentionally fails if ride_hailing already exists; it does not silently erase an existing database. Run the schema, routines, generated seed, warehouse and role scripts in order, then run the validation program. The README supplies commands and explains the dedicated instance setup.

The SQL scripts are the executable source of truth. create_logic.py regenerates procedure definitions, generate_data.py regenerates the same sample data, and run_validation.py reruns checks and collects query outputs. build_reports.py reads those outputs and the actual information_schema export to create both LaTeX versions. The supplied .tex files can also be compiled directly with XeLaTeX.

The successful verification used MySQL '''+D['version'][0]['version']+''' in an isolated temporary directory with TCP networking disabled. The local sandbox could not initialize or access the server normally; the database was therefore run outside that restriction with access limited to its local socket. This is an environment detail, not an unexecuted-test exception. All published checks actually ran.

The report includes selected SQL and result tables for readability. Full scripts, raw query outputs, test records and a server-derived data dictionary are supplied so that design claims can be checked independently.''',
'''使用独立的 MySQL 8.4 实例，确保没有同名 schema。建库脚本在 ride_hailing 已存在时会报错，不会自动清空已有数据库。按顺序运行结构、过程、生成数据、仓库和角色脚本，再执行验证程序。README 提供完整命令及独立实例说明。

SQL 文件是可执行的依据。create_logic.py 生成过程定义；generate_data.py 重新生成相同数据；run_validation.py 运行检查并导出结果；build_reports.py 读取这些结果和服务器数据字典，生成两个 LaTeX 版本。也可以直接使用交付的 .tex 文件编译 PDF。

成功验证使用 MySQL '''+D['version'][0]['version']+'''，数据放在独立临时目录，关闭 TCP 网络监听。受限环境无法正常初始化和连接服务器，因此在该限制之外通过本地 socket 执行。这是运行环境说明，不代表测试未运行；所有报告中的检查均已实际执行。

报告只展示必要的 SQL 和结果以便阅读，同时提供完整脚本、原始查询输出、测试记录和由数据库导出的数据字典，使读者能独立核验设计结论。''',table(['File or directory','Purpose'],[['report_en.pdf / report_zh.pdf','English report and Chinese counterpart'],['source/report_en.tex / report_zh.tex','Editable LaTeX sources'],['sql/01_schema.sql … 07_report_demonstrations.sql','Operational schema, lifecycle, data, warehouse, queries, role'],['scripts/','Generation, validation, report build and execution helpers'],['results/validation.json','32 pass/fail records and error evidence'],['results/query_results.json and *.tsv','Actual query outputs, including EXPLAIN'],['results/report_evidence.json','Table samples and CRUD results'],['figures/','Four diagrams: PDF, SVG, PNG and editable draw.io'],['results/data_dictionary.tsv','Executed column metadata'],['README.md','Reproduction instructions and compatibility notes']]))
from revision_content import revise
P=revise(P,R,table,code,esc)

PRE=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\usepackage[fontset=none]{ctex}
\setmainfont{texgyrepagella-regular.otf}[BoldFont=texgyrepagella-bold.otf,ItalicFont=texgyrepagella-italic.otf,BoldItalicFont=texgyrepagella-bolditalic.otf]
\setsansfont{texgyreheros-regular.otf}[BoldFont=texgyreheros-bold.otf]
\setmonofont{lmmono10-regular.otf}[Scale=.87,BoldFont=lmmonolt10-bold.otf,ItalicFont=lmmono10-italic.otf,BoldItalicFont=lmmonolt10-boldoblique.otf]
\setCJKmainfont{FandolSong-Regular.otf}[BoldFont=FandolSong-Bold.otf]
\setCJKsansfont{FandolHei-Regular.otf}
\setCJKmonofont{FandolFang-Regular.otf}
\usepackage{booktabs,tabularx,array,longtable,amsmath,graphicx,xcolor,pdfpages}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,calc}
\usepackage{listings,enumitem,fancyhdr,titlesec}
\usepackage{xurl,tocloft}
\setlength{\cftbeforesecskip}{4pt}
\usepackage[unicode,hidelinks]{hyperref}
\definecolor{accent}{HTML}{1D4B60}
\definecolor{soft}{HTML}{F0F4F6}
\hypersetup{pdftitle={网约车的数据库设计},pdfauthor={}}
\titleformat{\section}{\Large\bfseries\color{accent}}{\thesection}{.65em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{.6em}{}
\titlespacing*{\section}{0pt}{0pt}{12pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{7pt}
\renewcommand{\arraystretch}{1.3}
\setlength{\tabcolsep}{4pt}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\setlist{nosep,leftmargin=1.5em}
\lstset{basicstyle=\ttfamily\small,breaklines=true,columns=fullflexible,keepspaces=true,showstringspaces=false,backgroundcolor=\color{soft},frame=single,rulecolor=\color{soft},xleftmargin=6pt,xrightmargin=6pt,aboveskip=8pt,belowskip=8pt}
\pagestyle{fancy}\fancyhf{}\fancyfoot[C]{\small\thepage}
\fancyhead[L]{\small\sffamily Ride Hailing Database Design}
\fancyhead[R]{\small\sffamily Relational design and validation}
\renewcommand{\headrulewidth}{.3pt}
\emergencystretch=2em
\raggedbottom
\begin{document}
\begin{titlepage}\thispagestyle{empty}\centering\vspace*{.34\textheight}
{\fontsize{28}{36}\selectfont 网约车的数据库设计\par}
\end{titlepage}
\pagenumbering{roman}
\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage
\pagenumbering{arabic}
'''

ZH_CELLS={'Requirement / 需求': '需求',
 'Objects and verification / 对象与验收': '数据对象与验证',
 'Shared identity and overlapping roles': '共享身份与重叠角色',
 'Vehicle and insurance records': '车辆与保险记录',
 'Multiple shifts per day': '一天多次轮班',
 'Request and assign a vehicle': '下单与车辆分配',
 'Mutually exclusive terminal outcomes': '互斥的最终结果',
 'Fare components and two-sided feedback': '费用组成与双向评价',
 'Operational and analytical queries': '运营与分析查询',
 'Reproducible implementation': '可复现实现',
 'app_user, passenger, driver; one overlapping account': 'app_user、passenger、driver；覆盖双角色账号',
 'vehicle, insurance_policy; immutable owner and date checks': 'vehicle、insurance_policy；归属不变与日期检查',
 'driver_shift; composite key and chronological checks': 'driver_shift；复合键与时间顺序',
 'trip; request default, driver/vehicle match': 'trip；默认下单状态，司机车辆匹配',
 'completed_trip, cancelled_trip; procedures and guards': 'completed_trip、cancelled_trip；过程与保护触发器',
 'surcharge, review; exact decimals and score checks': 'surcharge、review；精确金额与评分检查',
 'views and warehouse; counts, sums and query outputs': '视图与仓库；行数、金额和查询结果',
 'seed, SQL, tests and saved machine-readable results': '随机种子、SQL、测试和可读取的结果文件',
 'B per A': '每个 A 的 B 数',
 'A per B': '每个 B 的 A 数',
 'Rule': '规则',
 'Partial overlapping specialization': '部分、可重叠特化',
 'Same person can hold both roles': '同一人可同时拥有两种角色',
 'Owner fixed during observation': '观察期内归属固定',
 'Multiple policies/history allowed': '允许多份保单及历史记录',
 'Start time is a partial identifier': '开始时间为局部标识符',
 'One account requests each trip': '每单由一个账号请求',
 'Required after assignment': '派单后必须存在',
 'Only completed outcome': '只表示完成结果',
 'Only cancelled outcome': '只表示取消结果',
 'One row may contain both scores': '一行可包含双方评分',
 'Absent row means zero surcharge': '没有记录表示无附加费',
 'Relation': '关系',
 'Primary key': '主键',
 'Foreign key targets': '外键引用对象',
 'Column': '字段',
 'SQL type': 'SQL 类型',
 'Null': '可为空',
 'Key': '键标记',
 'Candidate keys': '候选键',
 'Functional dependencies': '函数依赖',
 'Either key → all other attributes': '任一候选键 → 其余全部属性',
 'Composite key → shift_end': '复合键 → shift_end',
 'trip_id → every remaining attribute': 'trip_id → 其余全部属性',
 'trip_id → both scores and comments': 'trip_id → 双方评分和评论',
 'Operational table': '运营表',
 'Rows': '行数',
 'Area': '类别',
 'Observed checks': '实际检查',
 'Outcome': '结果',
 'Pass': '通过',
 'Keys and references': '键与引用',
 'Duplicate ID, duplicate review, missing parent, protected deletion': '重复编号、重复评价、无效父记录、受限删除',
 'Domains': '值域',
 'Out-of-range score, empty feedback, negative amount, required name': '越界评分、空评价、负金额、姓名必填',
 'Time': '时间',
 'Shift end, start before request, completion before start': '轮班结束、开始早于请求、完成早于开始',
 'Workflow': '流程',
 'Owner immutability, wrong driver, disjoint outcomes, terminal state': '归属固定、错误司机、互斥结果、终态限制',
 'Transactions': '事务',
 'Partial write undone; parent state retained; success path': '撤销部分写入、保留原状态、成功路径',
 'Concurrency': '并发',
 'Two completions: exactly one commit': '两次完成请求中恰好一次提交',
 'Privileges': '权限',
 'Direct status write denied; authorized request/cancel allowed': '禁止直接改状态，允许授权下单和取消',
 'Reconciliation': '核对',
 '200 trips, state/detail alignment, no fanout, warehouse count/fare': '200 '
                                                                       '单、状态详情一致、连接无放大、仓库行数金额一致',
 'Coverage': '样例覆盖',
 'Overlapping role, two shifts per day, CRUD cleanup': '重叠角色、同日双轮班、增改删清理',
 'State': '状态',
 'Trips': '行程数',
 '% of all requests': '占全部请求比例 %',
 'Driver': '司机',
 'Completed': '完成单数',
 'Gross fare': '总费用',
 'Mean score': '平均评分',
 'Scored': '评分数',
 'Year': '年',
 'Month': '月',
 'Model': '车型',
 'Fare': '费用',
 'Source': '资料',
 'Applied concepts': '应用概念',
 'Five development components and depth/reliability criteria': '五个开发环节及深度、可靠性要求',
 'Domains, keys, integrity and business context': '值域、键、完整性与业务背景',
 'Entities, attributes, cardinality, weak entities': '实体、属性、基数与弱实体',
 'Partial/total and overlapping/disjoint specialization': '部分/全部与重叠/互斥特化',
 'Entity/relationship/subtype mapping to relations': '实体、联系和子类到关系的映射',
 'Functional dependencies, 1NF, 2NF, 3NF and BCNF': '函数依赖及 1NF、2NF、3NF、BCNF',
 'MySQL DDL, constraints and CRUD': 'MySQL DDL、约束及增删改查',
 'NULL, joins, aggregation, filtering and subqueries': 'NULL、连接、聚合、筛选和子查询',
 'Views, advanced queries and transactions': '视图、高级查询和事务',
 'OLTP/OLAP, star schema, ROLLUP and LAG': 'OLTP/OLAP、星型模型、ROLLUP 和 LAG',
 'File or directory': '文件或目录',
 'Purpose': '用途',
 'English report and Chinese counterpart': '英文报告与中文对照版',
 'Editable LaTeX sources': '可编辑的 LaTeX 源码',
 'Operational schema, lifecycle, data, warehouse, queries, role': '运营结构、生命周期、数据、仓库、查询及角色',
 'Generation, validation, report build and execution helpers': '生成、验证、报告编译及运行辅助程序',
 '32 pass/fail records and error evidence': '32 项测试结果及错误证据',
 'Actual query outputs, including EXPLAIN': '实际查询输出，含 EXPLAIN',
 'Executed column metadata': '实际字段元数据',
 'Reproduction instructions and compatibility notes': '复现说明与兼容性说明'}

ZH_CELLS.update({'Initial item': '初始项目', 'Current representation': '当前表达', 'Reason': '理由', 'Unfinished trip': '未完成行程', 'Trip status plus CancelledTrip': '行程状态与取消详情分开', 'Waiting and active trips have no cancellation time': '待接单和进行中的行程没有取消时间', 'Driver and vehicle on trips': '行程中的司机与车辆', 'Trip.plate plus derived driver': 'Trip.plate 与派生司机', 'Fixed ownership makes duplicate driver storage redundant': '固定车辆归属使重复保存司机造成冗余', 'Shift identified by driver/date': '司机与日期识别轮班', 'Driver plus shift_start': '司机与开始时间', 'A driver can have multiple shifts on one date': '同一司机一天可以有多个班次', 'Independent review identifier': '独立评价编号', 'Completed trip identifier': '完成行程编号', 'One bilateral review record per completed trip': '每条完成行程最多一条双向评价记录', 'Vehicle insurance treated as weak': '车辆保险视作弱实体', 'Independent policy_id': '独立保单编号', 'The policy has its own globally unique identifier': '保单有自己的全局唯一标识符', 'Payment, settlement and live maps': '支付、结算和实时地图', 'Gray external/future function boxes': '灰色外围或未来功能框', 'Retain context without claiming unimplemented services': '保留背景但不宣称实现未开发的服务', 'Symbol': '符号', 'Meaning': '含义', 'Rectangle / double rectangle': '矩形／双矩形', 'Regular entity / identification-dependent entity': '普通实体／身份依赖型实体', 'Ellipse / underline': '椭圆／下划线', 'Attribute / entity identifier': '属性／实体标识符', 'Dashed underline': '虚线下划线', 'Partial identifier within an owner': '所有者范围内的局部标识符', 'Diamond / double diamond': '菱形／双菱形', 'Relationship / identifying relationship': '联系／识别联系', 'Circle + bar; two bars': '圆圈加竖线；双竖线', 'Zero or one; exactly one': '零或一个；恰好一个', 'Circle + crow foot': '圆圈加乌鸦脚', 'Zero or many': '零至多个', 'o / d in a circle': '圆内 o／d', 'Overlapping / disjoint specialization': '重叠／互斥特化', 'Single supertype connector': '父实体单线连接', 'Partial specialization': '部分特化', 'Table samples and CRUD results': '表样例及增删改查结果', 'Four diagrams: PDF, SVG, PNG and editable draw.io': '四类图：PDF、SVG、PNG 及可编辑 draw.io'})

from structured_report import render_reports
render_reports(P,R,PRE,ZH_CELLS,table,code,esc,paras)
