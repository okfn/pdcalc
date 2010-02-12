'''Fast (en-masse via sql) PD calculations.
'''
import logging

from pdw.pd import OLDEST_PERSON

logger = logging.getLogger(__name__)

FAST_PD_KEY = u'pd.pdw.fast'
def fast_pd(extras_key=FAST_PD_KEY):
    import pdw.model as model
    import pdw.search
    from sqlalchemy import sql
    import time

    now = 2008
    pd_year = now - 70
    least_age_at_publication = 20
    publication_pd = pd_year - (OLDEST_PERSON - least_age_at_publication)
    # TODO: multi authors
    # Rather than use insert into use select then insert
    ptab = model.person_table
    itab = model.item_table
    q = sql.select([itab.c.id],
        from_obj=pdw.search.QueryHelper.item_person()
        )
    qout = q.where(sql.or_(
        ptab.c.death_date_ordered <= pd_year,
        ptab.c.birth_date_ordered <= pd_year - OLDEST_PERSON,
        itab.c.date_ordered <= publication_pd,
        ))
    qin = q.where(sql.or_(
        ptab.c.death_date_ordered > pd_year,
        ptab.c.birth_date_ordered > pd_year - 30,
        ))
    start = time.time()
    # results = [ r[0] for r in q.execute().fetchall() ]
    def get_inserts(results, value):
        inserts = []
        for row in results:
            tdict = { 'table': u'item',
                'fkid': row[0],
                'key': extras_key,
                'value': value }
            inserts.append(tdict)
        return inserts

    cmd = model.extra_table.delete(model.extra_table.c.key==extras_key)
    out = cmd.execute()
    logger.info('Deleting all existing entries with key: %s' % extras_key)

    inserts = get_inserts(qout.execute().fetchall(), 1.0)
    if inserts:
        model.metadata.bind.execute(model.extra_table.insert(), inserts)
    logger.info('Completed PD items')
    logger.info('Time elapsed: %s' % (time.time() - start))

    inserts = get_inserts(qin.execute().fetchall(), 0.0)
    if inserts:
        model.metadata.bind.execute(model.extra_table.insert(), inserts)
    logger.info('Completed Non-PD items')
    logger.info('Time elapsed: %s' % (time.time() - start))


FAST_PD_YEAR_KEY = u'pd_year.life_plus_70'
def fast_pd_year(extras_key=FAST_PD_YEAR_KEY):
    '''New approach:

        compute pd_year for each person/item/work

        key: pd_year.life_plus_70

        if death_date: pd_year = death_date + 70
        elif birth_date: pd_year = birth_date + OLDEST_PERSON + 70
        else: pd_year = date_of_publication + OLDEST_PERSON - LEAST_AGE_AT_PUBLICATION + 70

    # would be nice to use sql directly but can't generate primar_key id
    insert into extra select item.id, person.death_date_ordered from
    item join item_2_person on item.id = item_2_person.item_id join person on
    item_2_person.person_id = person.id where person.death_date_ordered is not
    null;
    '''
    import pdw.model as model
    import pdw.search
    from sqlalchemy import sql
    import time

    least_age_at_publication = 20
    post_death_term = 70
    # TODO: multi authors
    # Rather than use insert into use select then insert
    ptab = model.person_table
    itab = model.item_table
    q = sql.select([itab.c.id, ptab.c.death_date_ordered],
        from_obj=pdw.search.QueryHelper.item_person()
        )
    q = q.where(ptab.c.death_date_ordered!=None)
    # more complex algorithm
    q_cmplx = sql.select([itab.c.id, sql.func.coalesce(ptab.c.death_date_ordered,
        ptab.c.birth_date_ordered+OLDEST_PERSON,
        itab.c.date_ordered + (OLDEST_PERSON - least_age_at_publication)) +
        post_death_term
        ],
        from_obj=pdw.search.QueryHelper.item_person()
        )
    start = time.time()
    def get_inserts(results):
        inserts = []
        for row in results:
            tdict = { 'table': u'item',
                'fkid': row[0],
                'key': extras_key,
                'value': row[1]}
            inserts.append(tdict)
        return inserts

    cmd = model.extra_table.delete(model.extra_table.c.key==extras_key)
    out = cmd.execute()
    logger.info('Deleting all existing entries with key: %s' % extras_key)

    # before we begin may need to update extra_id_seq
    # maxval = select max(id) + 1 from extra;
    # select setval('extra_id_seq', maxval);

    inserts = get_inserts(q.execute().fetchall())
    if inserts:
        model.metadata.bind.execute(model.extra_table.insert(), inserts)
    logger.info('Completed')
    logger.info('Time elapsed: %s' % (time.time() - start))


