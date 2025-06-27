"""
Course: CSE 351, week 10
File: functions.py
Author: Fiona Barnett

4. Meets Requirements: Implemented 2 required functions and the bonus one along with the speed-up explanations provided

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

This code builds a family tree using a depth-first search, moving upward through parents and downward through children. 
To speed it up, I used Python’s threading module so that each person related to a family (husband, wife, and children) is 
processed in a separate thread. This allows the tree to grow in multiple directions at the same time, rather than waiting 
for one branch to finish before starting another. A lock is used to make sure the shared tree isn’t modified by multiple 
threads at once, which prevents duplicate entries or data issues. This parallel approach significantly reduces the time 
it takes to build large family trees.


Describe how to speed up part 2

This function builds the family tree using a breadth-first approach. It speeds things up by creating a new thread every time 
a new family is found, so different parts of the tree can be built at the same time instead of one after the other. 
For each family, it grabs the husband, wife, and kids, adds them to the tree if they aren’t already there, and then spawns 
new threads to go up to the parents and down to the children. A lock is used to avoid race conditions when updating the tree, 
and a queue keeps track of all threads so we can wait for everything to finish at the end. This parallel setup makes the 
whole process a lot faster, especially with big trees.


Extra (Optional) 10% Bonus to speed up part 3

This version also does BFS, but it’s built way better than my earlier one. Instead of making a new thread every time I find a family, 
it starts with just 5 worker threads that stay running the whole time. Each thread pulls a family from the queue, processes it, 
adds the people, and puts any new families it finds back in the queue. This keeps things way more controlled and avoids constantly 
creating threads, which slows things down and wastes resources. If I want more speed, I can just bump up the number of workers. 
So it ends up being just as fast (or faster) than my old BFS version, but it’s cleaner, more efficient, and easier to scale.
(Takes about 30s to run with 5 threads)

"""
from common import *
import queue
import threading

tree_lock = threading.Lock()

def process_person(person_id, tree: Tree, threads: list, recurse_on_family=False):
    if not person_id:
        return

    person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
    if not person_data:
        return

    person = Person(person_data)
    with tree_lock:
        if tree.does_person_exist(person_id):
            return
        tree.add_person(person)

    next_id = person.get_familyid() if recurse_on_family else person.get_parentid()
    if next_id:
        t = threading.Thread(target=depth_fs_pedigree, args=(next_id, tree))
        t.start()
        threads.append(t)


def depth_fs_pedigree(family_id, tree: Tree):
    threads = []

    family_data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    if not family_data:
        return

    family = Family(family_data)

    with tree_lock:
        if tree.does_family_exist(family_id):
            return
        tree.add_family(family)

    # Process husband and wife
    process_person(family.get_husband(), tree, threads, recurse_on_family=False)
    process_person(family.get_wife(), tree, threads, recurse_on_family=False)

    # Process children
    for child_id in family.get_children():
        process_person(child_id, tree, threads, recurse_on_family=True)

    for t in threads:
        t.join()

# -----------------------------------------------------------------------------

def worker(fam_id, family_queue, tree: Tree):
    with tree_lock:
        if tree.does_family_exist(fam_id):
            return

    family_data = get_data_from_server(f'{TOP_API_URL}/family/{fam_id}')
    if not family_data:
        return

    family = Family(family_data)
    with tree_lock:
        tree.add_family(family)

    # Process husband
    husband_id = family.get_husband()
    if husband_id:
        husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
        if husband_data:
            husband = Person(husband_data)
            with tree_lock:
                if not tree.does_person_exist(husband_id):
                    tree.add_person(husband)
            parent_fam = husband.get_parentid()
            if parent_fam:
                spawn_worker(parent_fam, family_queue, tree)

    # Process wife
    wife_id = family.get_wife()
    if wife_id:
        wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')
        if wife_data:
            wife = Person(wife_data)
            with tree_lock:
                if not tree.does_person_exist(wife_id):
                    tree.add_person(wife)
            parent_fam = wife.get_parentid()
            if parent_fam:
                spawn_worker(parent_fam, family_queue, tree)

    # Process children
    for child_id in family.get_children():
        child_data = get_data_from_server(f'{TOP_API_URL}/person/{child_id}')
        if child_data:
            child = Person(child_data)
            with tree_lock:
                if not tree.does_person_exist(child_id):
                    tree.add_person(child)
            child_family = child.get_familyid()
            if child_family:
                spawn_worker(child_family, family_queue, tree)

def spawn_worker(fam_id, family_queue, tree):
    t = threading.Thread(target=worker, args=(fam_id, family_queue, tree))
    t.start()
    family_queue.put(t)

def breadth_fs_pedigree(family_id, tree: Tree):
    family_queue = queue.Queue()
    spawn_worker(family_id, family_queue, tree)

    # Wait for all threads to finish
    while not family_queue.empty():
        thread = family_queue.get()
        thread.join()
  
# -----------------------------------------------------------------------------
def limited_worker(family_queue, tree: Tree):
    global tree_lock
    while True:
        fam_id = family_queue.get()
        if fam_id is None:
            family_queue.task_done()
            break

        with tree_lock:
            if tree.does_family_exist(fam_id):
                family_queue.task_done()
                continue

        family_data = get_data_from_server(f'{TOP_API_URL}/family/{fam_id}')
        if not family_data:
            family_queue.task_done()
            continue

        family = Family(family_data)
        with tree_lock:
            tree.add_family(family)

        # Process husband
        husband_id = family.get_husband()
        if husband_id:
            husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
            if husband_data:
                husband = Person(husband_data)
                with tree_lock:
                    if not tree.does_person_exist(husband_id):
                        tree.add_person(husband)
                parent_fam = husband.get_parentid()
                if parent_fam:
                    family_queue.put(parent_fam)

        # Process wife
        wife_id = family.get_wife()
        if wife_id:
            wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')
            if wife_data:
                wife = Person(wife_data)
                with tree_lock:
                    if not tree.does_person_exist(wife_id):
                        tree.add_person(wife)
                parent_fam = wife.get_parentid()
                if parent_fam:
                    family_queue.put(parent_fam)

        # Process children
        for child_id in family.get_children():
            child_data = get_data_from_server(f'{TOP_API_URL}/person/{child_id}')
            if child_data:
                child = Person(child_data)
                with tree_lock:
                    if not tree.does_person_exist(child_id):
                        tree.add_person(child)
                child_family = child.get_familyid()
                if child_family:
                    family_queue.put(child_family)

        family_queue.task_done()

def breadth_fs_pedigree_limit5(family_id, tree:Tree, MAX_THREADS = 5):
    global tree_lock

    family_queue = queue.Queue()
    family_queue.put(family_id)

    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=limited_worker, args = (family_queue, tree))
        t.start()
        threads.append(t)

    family_queue.join()

    for _ in threads:
        family_queue.put(None)

    for t in threads:
        t.join()