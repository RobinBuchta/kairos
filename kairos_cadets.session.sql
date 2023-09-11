Select * from node2id WHERE index_id BETWEEN 0 AND 100; --Limit 3;


select * from file_node_table LImit 3;
select * from netflow_node_table LImit 3;
select * from subject_node_table LImit 3;
Select * from node2id limit 3;
Select count(*) from subject_node_table;  -- 224146

Select count(*) from netflow_node_table; -- 155322

Select count(*) from file_node_table; --234245

Select count(*) from node2id; --268242

Select count(distinct path) from file_node_table; -- 198235

Select count(distinct path) from netflow_node_table; -- 198235
Select count(distinct exec) from subject_node_table; -- 130
Select count(distinct node_uuid) from subject_node_table; -- 224146

Select distinct exec from subject_node_table;



Select count(*) from node2id WHERE node_type = 'file'; --198235
Select count(*) from node2id WHERE node_type = 'subject'; -- 130
Select count(*) from node2id WHERE node_type = 'netflow'; -- 69877

Select * from event_table limit 10;

Select distinct operation from event_table;
Select count(distinct operation) from event_table; -- 20
Select count(*) from event_table; -- 29727441


Delete from event_table;
Delete from file_node_table;
Delete from netflow_node_table;
Delete from node2id;
Delete from subject_node_table;


select * from subject_node_table LIMIT 10;
select count(*) from subject_node_table; -- 279369
select COUNT(DISTINCT(tgid)) from subject_node_table; --32458
select COUNT(DISTINCT("cmdLine")) as cmdline from subject_node_table; -- 1570 
select COUNT(DISTINCT(path)) from subject_node_table; --169

SELECT COUNT(DISTINCT CONCAT(tgid, ' ', "cmdLine", ' ', path)) as unique_combinations_count FROM subject_node_table; --135475 
SELECT DISTINCT CONCAT(tgid, ' ', "cmdLine", ' ', path) as unique_combinations_count FROM subject_node_table;