def delete_customer(payload, client):
    # Fetch back the latest record from staging that needs to be updated
    query = """
    select customer_id, customer_number, first_name, last_name,
    date(createddate)||'T'||time(createddate) as createddate,
    from (select *,row_number() over(partition by customer_number order by lastmodifieddate desc) as rn from staging.repl_customers)
    where rn = 1
    and customer_id='%s'""" % payload["ChangeEventHeader"]["recordIDs"][0]
    query_job = client.query(query)
    records = [dict(row) for row in query_job]
    #We will need to indicate that this is a 'Delete'
    #and set the effective_from to the lastmodifieddate in the payload
    update = {"CRUD_flag": "D", "lastmodifieddate":payload["LastModifiedDate"]}
    records[0].update(update)
    errors = client.insert_rows_json("steadfast-task-363413.staging.repl_customers", records)
    if errors != []:
        print("Encountered errors while inserting rows: {}".format(errors))
