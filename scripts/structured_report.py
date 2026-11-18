"""Five-chapter report, explicit normalization derivation, and confirmed team details."""
import csv,json,re

MEMBERS=[('1','226040384','Lin Shuaiyu'),('2','226040421','Cai Ruihe'),('3','226040351','Li Songzi'),('4','226040373','Wen Zhang'),('5','226040424','Zhang Xiujie'),('6','122090871','Jin Conghao')]
TITLE='Ride-Hailing Platform Database Design'

def render_reports(P,R,PRE,ZH_CELLS,table,code,esc,paras):
    items={x[0]:x for x in P}
    meta=list(csv.DictReader((R/'results/data_dictionary.tsv').read_text().splitlines(),delimiter='\t'))
    core=['app_user','passenger','driver','vehicle','insurance_policy','driver_shift','trip','completed_trip','cancelled_trip','review','surcharge']
    attrs={t:[r['COLUMN_NAME'] for r in meta if r['TABLE_NAME']==t] for t in core}
    E=json.loads((R/'results/report_evidence.json').read_text())
    def tr(extra,lang):
        if lang=='zh':
            for a,b in sorted(ZH_CELLS.items(),key=lambda z:-len(z[0])):
                extra=re.sub(r'(?m)(^| & )'+re.escape(esc(a))+r'(?= & |\\\\)',lambda m:m.group(1)+esc(b),extra)
        return extra
    for lang in ['en','zh']:
        zh=lang=='zh'
        def pick(a,b):return b if zh else a
        def prose(a,b):
            if not a.strip() or not b.strip():raise ValueError('Both report languages require complete prose')
            return paras(pick(a,b))
        def tbl(enheaders,zhheaders,rows,widths=None):
            return table(pick(enheaders,zhheaders),[[pick(*c) if isinstance(c,tuple) else c for c in row] for row in rows],widths)
        def heading(a,b):return '\\subsection{'+esc(pick(a,b))+'}\n'
        def subhead(a,b):return '\\subsubsection*{'+esc(pick(a,b))+'}\n'
        def section(a,b):return '\\clearpage\n\\section{'+esc(pick(a,b))+'}\n'
        def block(name,with_prose=True):
            en,zt,ep,zp,extra=items[name]
            if 'Data dictionary' in name:
                extra=r'\begingroup\renewcommand{\arraystretch}{1.08}\titlespacing*{\subsection}{0pt}{7pt}{3pt}'+extra+r'\endgroup'
            # In the restructured report these blocks flow continuously.
            ep=ep.replace('on the next page','below').replace('previously described','subsequently described')
            zp=zp.replace('下一页','下文').replace('下一页','下文')
            if not zh:
                extra=extra.replace('Requirement / 需求','Requirement').replace('Objects and verification / 对象与验收','Objects and verification')
                extra=re.sub(r' / [\u4e00-\u9fff]+', '', extra)
            return (paras(zp if zh else ep) if with_prose else '')+tr(extra,lang)+'\n'
        pre=PRE[:PRE.index(r'\begin{document}')]
        pre=pre.replace('pdftitle={网约车的数据库设计}','pdftitle={'+TITLE+'}')
        pre+=r'\setcounter{tocdepth}{1}\titlespacing*{\subsection}{0pt}{13pt}{7pt}\titlespacing*{\subsubsection}{0pt}{10pt}{5pt}'+'\n'
        if zh:pre=pre.replace('Ride Hailing Database Design','网约车平台数据库设计').replace('Relational design and validation','G6 · 关系设计与验证')
        else:pre=pre.replace('Relational design and validation','G6 · Design and validation')
        cover=(r'\begin{document}\begin{titlepage}\thispagestyle{empty}\centering\vspace*{2cm}'+'\n'+
               r'{\fontsize{26}{34}\selectfont\bfseries Ride-Hailing Platform\\[4pt]Database Design\par}\vspace{1.1cm}'+'\n'+
               r'{\Large Group G6\par}\vspace{1.2cm}'+'\n'+
               table(['Member','Student ID','Name'],MEMBERS,r'p{2cm}p{4cm}p{4cm}')+
               r'\end{titlepage}\pagenumbering{roman}'+'\n')
        if not zh:cover+=r'\renewcommand{\contentsname}{Contents}'+'\n'
        s=pre+cover+r'\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage\pagenumbering{arabic}'+'\n'
        s+=r'\section{'+pick('Introduction and Requirements Analysis','项目背景与需求分析')+'}\n'
        s+=heading('Business context and scope','业务背景与范围')+block('Purpose and business requirements')
        s+=heading('Requirements and functional structure','需求与功能结构')+block('Requirements and acceptance criteria')+block('Front-end and back-office functions')
        s+=section('Conceptual Design','概念设计')
        s+=heading('Complete ER/EER model','完整 ER/EER 模型')+block('Complete conceptual ER/EER model')
        s+=heading('Relationships, participation and lifecycle','联系、参与约束与生命周期')+block('Relationships and business meaning')+block('Specialization and trip lifecycle')
        s+=section('Relational Mapping and Step-by-Step Normalization','关系映射与逐步规范化')+r'\begingroup\setlength{\parskip}{4pt}\renewcommand{\arraystretch}{1.1}\lstset{aboveskip=5pt,belowskip=5pt}'+'\n'
        s+=heading('From the ER/EER diagram to initial relations','从 ER/EER 图到初始关系模式')
        s+=prose('''This chapter makes the design process explicit: map entities and relationships, write a provisional relational schema, inspect 1NF, remove partial dependencies for 2NF, remove transitive dependencies for 3NF, and then check every remaining determinant for BCNF. Each stage states what changes and what stays unchanged.

The starting schema below is a reconstructed design-stage worksheet used to explain the derivation. It is not a claim that these intermediate tables were executed in MySQL or copied verbatim from an earlier file. The actual database contains only the final schema. The worksheet retains the assigned driver in Trip0 alongside the vehicle, reflecting the original driver-to-trip association. The other entity mappings are kept intact. The 2NF section separately uses a clearly labeled counterexample to explain why driver descriptors should remain outside the shift relation; that counterexample is not an additional project table.''',
        '''本章把设计过程显式展开：先把实体和联系转换为关系，写出初始关系模式；再检查 1NF，消除部分依赖以达到 2NF，消除传递依赖以达到 3NF，最后检查所有决定因素是否满足 BCNF。每一步都明确哪些表改变、哪些表无需改变。

下面的初始模式是为说明推导而重建的设计工作稿，不代表这些中间表已经在 MySQL 执行过，也不声称逐字复制自历史文件。实际数据库只实现最终模式。工作稿在 Trip0 中同时保留车辆与所分配的司机，以对应原设计中的司机到行程联系，其余实体映射保持不变。2NF 一节另设明确标注的反例，解释司机描述属性为什么应保留在轮班关系之外；这个反例并不是新增的项目表。''')
        s+=tbl(['Diagram construct','Initial relational mapping'],['图中构造','初始关系转换'],[
          [('Regular entities and attributes','普通实体与属性'),('One relation per entity; atomic attributes become columns. AppUser, Driver, Vehicle and InsurancePolicy retain their own identifiers.','每个实体映射为一个关系，原子属性成为列；用户、司机、车辆和保单保留各自标识符。')],
          [('User-role specialization','用户角色特化'),('Passenger and Driver inherit the user key as PK/FK. Overlapping roles do not duplicate shared contact attributes.','乘客与司机继承用户键作为主外键；重叠角色不重复保存公共联系方式。')],
          [('Owns, Requests, Covers, Serves','拥有、请求、承保、服务联系'),('Place the one-side key on the many side. Vehicle gets driver_id; Trip gets passenger_id and optional plate; InsurancePolicy gets plate.','把一端的键放到多端：车辆保存司机编号，行程保存乘客编号和可空车牌，保险保存车牌。')],
          [('Identifying relationships','识别联系'),('Shift uses (driver_id, shift_start). Review and Surcharge inherit the completed-trip key.','轮班使用（司机编号，开始时间）；评价与附加费继承完成行程键。')],
          [('Trip-outcome specialization','行程结果特化'),('CompletedTrip and CancelledTrip inherit trip_id. Disjointness and status consistency are additional integrity rules.','完成与取消子类继承行程键；互斥及状态一致性另外用完整性规则保证。')]],r'p{3.3cm}X')
        s+=prose('''For example, a literal relationship relation Owns(driver_id, plate) has plate as its key because each vehicle has one owner. It can be absorbed into Vehicle by adding driver_id. Requests(passenger_id, trip_id) similarly places passenger_id in Trip; Covers(plate, policy_id) places plate in InsurancePolicy. Serves(plate, trip_id) supplies the optional Trip.plate. These are cardinality-based mapping choices, not separate normalization steps. There is no many-to-many relationship requiring an extra bridge table in this scope.''',
        '''例如，若先逐个联系落表，Owns(driver_id, plate) 因为一辆车只有一名所有者而以 plate 为键；把 driver_id 并入 Vehicle 即可吸收该联系。Requests(passenger_id, trip_id) 把乘客键放入 Trip；Covers(plate, policy_id) 把车牌放入保险表；Serves(plate, trip_id) 对应可空的 Trip.plate。这些是依据基数完成的映射选择，不是独立的规范化步骤。本范围没有需要额外桥接表的多对多联系。''')
        s+=r'\clearpage'+'\n'+subhead('Initial schema S0: relations before normalization','初始模式 S0：规范化前的关系清单')
        keys={'app_user':'user_id; alternate: phone','passenger':'passenger_id','driver':'driver_id; alternate: license_no','vehicle':'plate','insurance_policy':'policy_id','driver_shift':'(driver_id, shift_start)','trip':'trip_id','completed_trip':'trip_id','cancelled_trip':'trip_id','review':'trip_id','surcharge':'trip_id'}
        rows=[]
        for t in core:
            name={'trip':'Trip0'}.get(t,t)
            cols=attrs[t]+(['driver_id'] if t=='trip' else [])
            keytext=keys[t].replace('alternate:',pick('alternate:','备用键：'))
            rows.append([name,', '.join(cols)+'; '+pick('Key(s): ','候选键：')+keytext])
        s+=r'\begingroup\small\renewcommand{\arraystretch}{1.12}\begin{longtable}{p{3.1cm}p{12.1cm}}\toprule'+'\n'
        s+=esc(pick('Initial relation','初始关系'))+' & '+esc(pick('Attributes and candidate keys','属性与候选键'))+r'\\\midrule\endhead'+'\n'
        s+='\n'.join(esc(a)+' & '+esc(b)+r'\\[4pt]' for a,b in rows)
        s+=r'\bottomrule\end{longtable}\endgroup'+'\n'
        s+=prose('''DriverShift keeps only the driver key and the shift timestamps; driver descriptors remain in Driver. Trip0.driver_id is the driver of the assigned plate and is absent when there is no assignment. All other relations already use the attributes and identifiers of the final entity mapping. Thus the normal-form checks can distinguish an actual necessary change from relations that already meet the criteria.''',
        '''DriverShift 仅保留司机键和轮班时间戳，司机描述属性留在 Driver 中。Trip0.driver_id 表示所派车辆对应的司机，尚未分配车辆时为空。其余关系已经采用最终实体映射的属性和标识符，因此范式检查能够区分真正需要的修改与已经满足条件的关系。''')
        s+=heading('First normal form: scalar values and a valid key','第一范式：原子值与正确的键')
        s+=prose('''1NF requires each attribute value to belong to its atomic domain rather than contain a repeating group. S0 passes this check: one row describes one user, vehicle, policy, shift or trip; phone is one registered phone value; each timestamp is one DATETIME value. A driver with two vehicles is represented by two Vehicle rows, not a comma-separated vehicle list. Multiple shifts are represented by multiple DriverShift rows.

Therefore S1 = S0: no relation is split merely to claim a 1NF transformation. Correcting the shift identifier is a separate key-design issue. A date alone, even combined with driver_id, cannot identify two shifts by the same driver on one date. The mapping uses the actual start timestamp from the outset.''',
        '''1NF 要求每个属性值属于其原子值域，不能包含重复组。S0 满足这一检查：每行对应一个用户、车辆、保单、轮班或行程；phone 是一个登记电话号码；时间戳是单个 DATETIME 值。一个司机有两辆车时用两条 Vehicle 记录表示，而不是把两个车牌拼成一个字符串；多次轮班同样用多行表示。

因此 S1 = S0，无需为了声称“完成 1NF 转换”而强行拆表。轮班标识符的修正属于另一个键设计问题：同一司机一天有两班时，即便把 driver_id 与日期组合也无法唯一标识。因此从初始映射起就采用实际开始时间。''')
        shifts=E['driver_shift']['rows'][:2]
        s+=tbl(['driver_id','shift_start','shift_end'],['driver_id','shift_start','shift_end'],[[x['driver_id'],x['shift_start'],x['shift_end']] for x in shifts])
        s+=prose('These two rows come from the executed sample data. Both have the same driver and calendar date, but different shift_start values. Atomicity and uniqueness are related design checks; changing a deficient key alone is not a 1NF decomposition.',
        '这两条记录来自实际运行的样例数据，司机和日历日期相同，但 shift_start 不同。原子性与唯一性是相关但不同的设计检查；单纯修正一个不充分的键，不等于进行了 1NF 分解。')
        s+=heading('Second normal form: inspect composite-key dependencies','第二范式：检查复合键依赖')
        s+=prose("""2NF requires 1NF and requires every non-prime attribute to depend on each candidate key in full. DriverShift is the only S1 relation with a composite candidate key. Its key is (driver_id, shift_start), and its only non-prime attribute is shift_end. A driver has many shifts, and different drivers may start at the same time. Neither component alone determines shift_end; the complete pair does.

Every other S1 relation has only single-attribute candidate keys. Under the stated dependencies, none can exhibit a partial dependency on a nonempty proper subset of a key. Therefore S2 = S1: the mapped schema is already in 2NF. Keeping a table unchanged after a successful check is part of the normalization process, rather than a missing transformation.""", '2NF 要求关系满足 1NF，且每个非主属性都完全依赖每个候选键。DriverShift 是 S1 中唯一具有复合候选键的关系，键为（driver_id, shift_start），唯一非主属性是 shift_end。一个司机可以有多个轮班，不同司机也可能在同一时间开始工作，因此任一键分量都不能单独决定 shift_end，只有完整组合能够决定。\n\nS1 中其他关系的候选键均为单属性键。在所声明的依赖下，不存在对键的非空真子集的部分依赖。因此 S2 = S1，映射后的模式已经满足 2NF。检查通过后保持关系不变，同样是规范化过程的一部分，并不代表遗漏了转换步骤。')
        s+=code("""DriverShift(driver_id, shift_start, shift_end)
Candidate key: (driver_id, shift_start)
(driver_id, shift_start) -> shift_end
Neither driver_id nor shift_start alone determines shift_end.
Decision: retain DriverShift unchanged in S2.""")
        s+=subhead('Counterexample: what would break 2NF?','反例：什么设计会破坏第二范式？')
        s+=prose("""For comparison, suppose a convenience worksheet copied Driver's license_no and lifetime_km into each shift. Call it ShiftWide. This is an illustrative joined view of the existing sample records, not the actual initial schema and not a table that was implemented. Because license_no is unique and mandatory, its candidate keys would be (driver_id, shift_start) and (license_no, shift_start).

In ShiftWide, the non-prime lifetime_km depends on driver_id alone and on license_no alone. Both are proper subsets of candidate keys, so this counterexample violates 2NF. License_no itself is prime because it belongs to an alternative candidate key; the decisive 2NF violation is the non-prime mileage attribute.""", '作为对比，假设为了方便在每条轮班记录中复制 Driver 的 license_no 和 lifetime_km，得到 ShiftWide。它是把现有样例记录连接起来的说明性工作表，并不是实际初始模式，也不是已实现的表。由于 license_no 非空且唯一，这个反例的候选键将是（driver_id, shift_start）和（license_no, shift_start）。\n\n在 ShiftWide 中，非主属性 lifetime_km 分别只依赖 driver_id 或 license_no，而它们都是候选键的真子集，因此这个反例违反 2NF。license_no 自身属于备用候选键，是主属性；判定违反 2NF 的关键是非主属性累计里程的部分依赖。')
        s+=code("""Counterexample only:
ShiftWide(driver_id, shift_start, shift_end, license_no, lifetime_km)
driver_id -> license_no, lifetime_km
license_no -> driver_id, lifetime_km

Its correction would be:
Driver(driver_id, license_no, lifetime_km)
DriverShift(driver_id, shift_start, shift_end)
These are already the two relations in the mapped schema.""")
        driver1=next(x for x in E['driver']['rows'] if x['driver_id']==shifts[0]['driver_id'])
        s+=tbl(['driver_id','shift_start','license_no','lifetime_km'],['driver_id','shift_start','license_no','lifetime_km'],[[x['driver_id'],x['shift_start'],driver1['license_no'],driver1['lifetime_km']] for x in shifts])
        s+=prose("""The two reconstructed ShiftWide rows repeat the same registered mileage; a correction would have to update several shift rows. Separating Driver from DriverShift prevents that anomaly and permits a driver to exist before any shift is logged.

The illustrative decomposition is lossless because the intersection, driver_id, determines all Driver attributes. Joining the projections on driver_id reconstructs the original shift rows. Each listed dependency can be checked in one resulting relation, so it preserves the dependency set. The final schema already has this separation and a foreign key for the owner; no extra physical table or artificial 2NF split is needed.""", '两条重建的 ShiftWide 记录重复保存同一份登记里程，更正该值就需要更新多条轮班记录。将 Driver 与 DriverShift 分离，可以避免这种异常，并允许司机在尚未登记任何轮班时独立存在。\n\n该示例分解无损，因为两个关系的交集 driver_id 决定 Driver 的所有属性；按 driver_id 连接投影可以还原原始轮班行。列出的每个依赖都能在某个分解后的关系中检查，因此保持了依赖集。最终模式本来就包含这种分离及指向所有者的外键，无需增加物理表，也不需要人为制造一次 2NF 拆分。')
        s+=heading('Third normal form, BCNF and the final schema','第三范式、BCNF 与最终模式')
        s+=prose('''For every non-trivial dependency X -> A, 3NF requires X to be a superkey or A to be prime. In the assigned-trip part of Trip0, trip_id determines plate and fixed vehicle ownership gives plate -> driver_id. Plate is not a superkey of Trip0 because the same vehicle can serve several trips; driver_id is not a prime attribute. The dependency therefore violates 3NF, even though Trip0 has already passed 2NF.''',
        '''对每个非平凡依赖 X → A，3NF 要求 X 是超键，或者 A 是主属性。在 Trip0 已派车的记录中，trip_id 决定 plate，而固定车辆归属使 plate → driver_id 成立。同一车辆可以服务多个行程，所以 plate 不是 Trip0 的超键；driver_id 也不是主属性。因此该依赖违反 3NF，尽管 Trip0 已经通过 2NF 检查。''')
        s+=code('''Trip0(trip_id, passenger_id, plate, ..., status, driver_id)
trip_id -> plate
plate -> driver_id
Therefore: trip_id -> plate -> driver_id

Project into:
Trip(trip_id, passenger_id, plate, ..., status)
VehicleOwner(plate, driver_id)

VehicleOwner is already represented inside:
Vehicle(plate, driver_id, model, color, capacity)''')
        s+=prose('''Remove driver_id from Trip0 and use the existing Vehicle relation to determine the driver. For example, sample trip 1 uses DEMO001, and Vehicle assigns DEMO001 to driver 1. A duplicated Trip0.driver_id of 2 would contradict that fact; the final schema cannot store that contradictory duplicate. The dispatch procedure still accepts both identifiers and verifies their match.

For assigned trips, the decomposition is lossless because the intersection {plate} determines VehicleOwner. The dependency trip_id -> plate remains in Trip, plate -> driver_id remains in Vehicle, and their transitive implication is preserved across the design. The conceptual proof concerns assigned records with a present vehicle. Unassigned requests have no vehicle-owner association; in the SQL representation their plate is NULL. A LEFT JOIN retains those requests with a NULL derived driver. It would be incorrect to claim that an INNER JOIN preserves unassigned rows or to apply the classical no-NULL proof to them unchanged.

BCNF strengthens the determinant condition: every non-trivial determinant must be a superkey, even when the dependent attribute is prime. Driver satisfies it because both driver_id and license_no are candidate keys. AppUser similarly has user_id and phone. In DriverShift, the only stated non-trivial determinant is the complete pair (driver_id, shift_start). The remaining final relations have only their candidate-key dependencies under the stated assumptions. No further BCNF split is required after S3. The following table checks every final relation.''',
        '''从 Trip0 删除 driver_id，改由已有 Vehicle 表确定司机。例如实际样例的行程 1 使用 DEMO001，而 Vehicle 指明 DEMO001 对应司机 1。若重复保存的 Trip0.driver_id 写成 2，就与车辆记录矛盾；最终模式不再允许存储这份矛盾的重复值。派单过程仍接受司机和车牌两个参数，并检查是否匹配。

对已派车行程，两个投影的交集 {plate} 决定 VehicleOwner，因此分解无损。trip_id → plate 留在 Trip，plate → driver_id 留在 Vehicle，它们的传递推论仍被设计保留。这个概念层证明针对车辆已存在的分配记录。未派车请求尚无车辆归属联系，在 SQL 中用 plate 为 NULL 表示；LEFT JOIN 保留这些请求，并返回空的派生司机。不能声称 INNER JOIN 也能保留未派车记录，也不能把经典的无 NULL 分解证明原样套到这些行上。

BCNF 进一步要求每个非平凡决定因素都是超键，即便被决定属性是主属性也一样。Driver 的 driver_id 与 license_no 都是候选键，因此满足该条件；AppUser 的 user_id 与 phone 同理。DriverShift 唯一声明的非平凡决定因素是完整的（driver_id, shift_start）。其余最终关系在本项目假设下只有候选键决定的依赖。因此 S3 无需继续拆分即可达到 BCNF。下表逐一核对最终关系。''')
        s+=block('Functional dependencies and normal forms',False)
        s+=prose('''There are no additional asserted dependencies such as model -> capacity or distance -> fare. Vehicle capacity is recorded per vehicle, and fare includes components not determined by distance alone. The normal-form conclusion follows from the declared business semantics; a small dataset cannot establish all real-world functional dependencies.

Some changes are not normal-form decompositions. Separating CompletedTrip from CancelledTrip expresses disjoint outcomes. Keeping Surcharge separate expresses an optional one-to-one detail: merging its amount into CompletedTrip would not, by itself, violate BCNF. Giving Review one trip_id key enforces at most one bilateral review row per completed trip; an independent review_id plus UNIQUE(trip_id) could also be normalized. These choices should not be presented as necessary steps from 2NF to 3NF.''',
        '''这里没有额外声明 model → capacity 或距离 → 费用等依赖。容量按每辆车记录；费用还包含不能仅由距离确定的组成部分。范式结论来自已声明的业务语义，不能仅凭少量样例数据证明真实世界的一切函数依赖。

另外，有些改动不属于范式分解：分开完成与取消详情是在表达互斥结果；附加费单独保存是在表达可选的一对一详情，把 amount 并入 CompletedTrip 本身并不违反 BCNF；评价采用 trip_id 为键，是为了每单最多一条双向反馈，而独立 review_id 加 UNIQUE(trip_id) 也可以满足范式。不能把这些选择写成从 2NF 到 3NF 必须执行的拆分。''')
        s+=tbl(['Stage','Decision','Result'],['阶段','检查与处理','结果'],[
          ['S0 → S1',('Atomic values; correct shift identifier','原子值；正确的轮班标识符'),('Already 1NF; no split','已满足 1NF，不拆表')],
          ['S1 → S2',('Check the composite DriverShift key','检查 DriverShift 的复合键'),('Already 2NF; no split','已满足 2NF，无需拆分')],
          ['S2 → S3',('Remove plate -> driver_id from Trip0','消除 Trip0 中车牌到司机的传递依赖'),('Trip + existing Vehicle; 3NF','Trip + 已有 Vehicle，达到 3NF')],
          ['S3 → BCNF',('Inspect all non-trivial determinants','检查所有非平凡决定因素'),('No additional split; 11 final tables','无需继续分解，最终 11 张表')]],r'p{2.5cm}p{6.2cm}X')
        s+=prose('The final relational diagram below shows all 11 operational tables and every implemented column. PK, FK and UQ identify primary, foreign and alternate keys; ? marks a nullable column. Its fields are generated from the executed MySQL data dictionary and match the SQL implementation that follows.', '下面的最终关系图展示全部 11 张运营表及实现字段。PK、FK、UQ 分别表示主键、外键和备用唯一键，问号表示字段可空。图中的字段由实际执行的 MySQL 数据字典生成，与后续 SQL 实现一致。')+items['Complete relational schema diagram'][4]
        s+=r'\endgroup'+'\n'+section('Database Implementation and Validation','数据库实现与验证')
        s+=heading('Physical tables, constraints and creation SQL','物理表、约束与建表 SQL')+block('SQL implementation and integrity')+block('Creating the database and all core tables')
        s+=heading('Loaded data and executable SQL demonstrations','数据装载与 SQL 实际演示')+block('Synthetic dataset and reproducibility')+block('Displaying the created tables and structure')
        for name in ['Inserted data for users and roles','Inserted data for assets and shifts','Inserted data for trips and outcomes','Feedback, surcharge and joined results','Insertion, update and deletion with results']:
            s+=subhead(name,items[name][1])+block(name)
        s+=heading('Transactions, concurrency and validation','事务、并发与验证')+block('Transactions and concurrent requests')+block('Validation results')
        s+=section('Data Usage, Discussion and Conclusion','数据使用、讨论与结论')
        s+=heading('Operational queries and observed results','运营查询与实际结果')+block('Operational SQL and query semantics')+block('Observed results and interpretation')
        s+=heading('Analytical extension and reconciliation','分析扩展与数据核对')+block('Analytical star schema')+block('OLAP queries and reconciliation')
        s+=heading('Design limitations and conclusion','设计局限与结论')+block('Discussion and design limitations')
        s+=r'\appendix'+'\n'+section('Data Dictionary','数据字典')
        for name in ['Data dictionary for identities','Data dictionary for vehicles and shifts','Data dictionary for bookings','Data dictionary for outcomes']:
            s+=block(name, name=='Data dictionary for identities')
        s+=section('References and Reproduction','参考材料与复现说明')+block('Course alignment and references')+block('Reproduction and evidence inventory')
        s+=section('Team Responsibilities (Draft)','成员职责（草稿）')
        s+=prose('''This working table records the scope confirmed so far. It is not a peer-assessment score sheet and does not replace the separate Group Project Contribution Form referenced by the project requirements. Duties for the other five members remain unassigned in this draft; no contribution percentages are inferred.

Lin Shuaiyu confirmed responsibility for defining the overall report topic, requirements and business scope, conceptual ER/EER design, and logical design including relational mapping and normalization, up to the stage before concrete sample-data preparation. Possible later work on data generation, implementation or integration is not listed as a confirmed responsibility here.''',
        '''本工作表只记录目前已经确认的范围，不是互评分数表，也不替代项目要求提到的独立 Group Project Contribution Form。其余五位成员的职责在本稿中暂未分配，不推测贡献比例。

Lin Shuaiyu已确认负责总体报告主题确定、需求与业务范围分析、ER/EER 概念设计，以及关系映射和规范化等逻辑设计，范围截至具体样例数据准备之前。可能后续承担的数据生成、实现或整合工作，目前不列为已经确认的职责。''')
        rows=[]
        for n,sid,name in MEMBERS:
            duty=pick('Topic definition; requirements and scope; ER/EER design; relational mapping and normalization.','主题确定；需求与范围；ER/EER 设计；关系映射与规范化。') if n=='1' else pick('TBD - placeholder; not yet assigned.','待确认：暂留占位，尚未分配。')
            rows.append([name,sid,duty])
        s+=table(pick(['Member','Student ID','Confirmed scope / placeholder'],['成员','学号','已确认范围／占位']),rows,r'p{2.7cm}p{3cm}X')
        # Both reports share one schema, dataset, diagrams and member roster.
        s+=r'\end{document}'+'\n'
        (R/f'source/report_{lang}.tex').write_text(s)
    (R/'results/team_details.json').write_text(json.dumps({'group':'G6','title':TITLE,'members':[{'member':int(n),'student_id':sid,'name':name} for n,sid,name in MEMBERS],'responsibilities':'First member confirmed through logical design; all others TBD; data preparation and later work not allocated.'},ensure_ascii=False,indent=2))
    print('Generated aligned English and Chinese reports with 5 main chapters, 3 appendices and 6 members.')
