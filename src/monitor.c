// 1. Core BCC macro to handle standard kernel types
#define KBUILD_MODNAME "monitor"
#include <linux/ptrace.h>
#include <linux/sched.h>

/* * Professional Note: 
 * If you use <vmlinux.h>, you must remove the includes above.
 * However, BCC typically handles standard headers best 
 * by including them as shown below:
 */

struct data_t {
    u32 pid;
    char comm[TASK_COMM_LEN];
    char fname[256];
};

BPF_PERF_OUTPUT(events);