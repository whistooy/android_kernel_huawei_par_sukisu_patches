#!/usr/bin/env python3
"""Exercise the actual prepared OF fixup with mocked OF/allocation APIs.

Usage: python3 tests/test_par_fstab.py /path/to/prepared/kernel
This validates transformation/error paths, not kernel locking or phone boot.
"""
import pathlib
import subprocess
import sys
import tempfile

source = (pathlib.Path(sys.argv[1]) / 'drivers/of/base.c').read_text()
start = source.index('static int __init of_par_set_string(')
end = source.index('\n#endif', start)
functions = source[start:end]
harness = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define __init
#define GFP_KERNEL 0
struct property { char *name; void *value; int length; };
struct device_node { const char *name; struct property *status, *flags;
                     struct device_node *next; };
static struct device_node root, *children;
static int fail_alloc, alloc_index, updates, fail_update, absent, node_puts;
static void *kzalloc(size_t n, int unused) {
    if (++alloc_index == fail_alloc) return NULL;
    return calloc(1, n);
}
static char *kstrdup(const char *s, int unused) {
    if (++alloc_index == fail_alloc) return NULL;
    return strdup(s);
}
#define kfree free
#define pr_err(...) ((void)0)
static void release_property(struct property *p) {
    if (p) { free(p->name); free(p->value); free(p); }
}
static int of_update_property(struct device_node *n, struct property *p) {
    struct property **slot = !strcmp(p->name,"status") ? &n->status : &n->flags;
    assert(p->length == (int)strlen(p->value)+1);
    if (fail_update) return -EINVAL;
    release_property(*slot); *slot = p; ++updates; return 0;
}
static struct device_node *of_find_node_by_path(const char *path) {
    assert(!strcmp(path,"/firmware/android/fstab")); return absent ? NULL : &root;
}
#define for_each_child_of_node(parent, child) \
    for (child = children; child; child = child->next)
static int of_property_read_string(struct device_node *n,const char *key,const char **v) {
    assert(!strcmp(key,"fsmgr_flags"));
    if (!n->flags) return -EINVAL;
    *v = n->flags->value; return 0;
}
static void of_node_put(struct device_node *n) { assert(n == &root); ++node_puts; }
'''
tests = r'''
static void reset(void) {
    fail_alloc=alloc_index=updates=fail_update=absent=node_puts=0;
}
static void flags_case(const char *input, const char *expected) {
    struct device_node n = {.name="system"}; reset(); children=&n;
    assert(!of_par_set_string(&n,"fsmgr_flags",input)); updates=0;
    of_par_fixup_fstab(); assert(node_puts==1);
    assert(!strcmp(n.flags->value,expected));
    assert(updates == !!strcmp(input,expected));
    release_property(n.flags);
}
int main(void) {
    flags_case("wait,avb,first_stage_mount,logical", "wait,first_stage_mount,logical");
    flags_case("avb=vbmeta_system,wait,avb", "wait");
    flags_case("wait,avb_keys=/keys,notavb,avbfoo,verify", "wait,avb_keys=/keys,notavb,avbfoo,verify");
    flags_case("avb", ""); flags_case("", "");
    flags_case("wait,check,quota,formattable", "wait,check,quota,formattable");
    flags_case(",avb,,wait,", "wait");
    struct device_node n = {.name="preavs"}; reset(); children=&n;
    of_par_fixup_fstab(); assert(!strcmp(n.status->value,"disabled"));
    of_par_fixup_fstab(); assert(!strcmp(n.status->value,"disabled"));
    release_property(n.status); n.status=NULL;
    n.name="preavs_extra"; of_par_fixup_fstab(); assert(!n.status);
    reset(); absent=1; of_par_fixup_fstab(); assert(!node_puts && !updates);
    /* Every allocation in a changed flag path may fail without corrupting it. */
    for (int fail=1; fail<=5; ++fail) {
        reset(); n.name="vendor"; children=&n;
        assert(!of_par_set_string(&n,"fsmgr_flags","wait,avb"));
        alloc_index=0; fail_alloc=fail; of_par_fixup_fstab();
        assert(!strcmp(n.flags->value,"wait,avb"));
        release_property(n.flags); n.flags=NULL;
    }
    reset(); assert(!of_par_set_string(&n,"fsmgr_flags","wait,avb"));
    fail_update=1; of_par_fixup_fstab(); assert(!strcmp(n.flags->value,"wait,avb"));
    release_property(n.flags); n.flags=NULL;
    node_puts=0; /* no ownership left in the mock */
    printf("PAR fstab: token preservation, exact node match, lengths, failures passed\n");
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='par-fstab-test-') as work:
    c = pathlib.Path(work) / 'test.c'
    exe = pathlib.Path(work) / 'test'
    c.write_text(harness + functions + tests)
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Wno-unused-parameter',
                    '-fsanitize=address,undefined', '-g', str(c), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
