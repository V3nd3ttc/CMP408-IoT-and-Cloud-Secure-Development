#include <linux/module.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/fs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Martin Zhelev");
MODULE_DESCRIPTION("Button Press Kernel Module");

// Variables for WatchDog script
#define SIG_RUN 20
#define INIT_WATCHDOG 0x65
#define REM_WATCHDOG 0x66
static struct task_struct *task = NULL;

#define GPIO_NUMBER 1
#define MAJOR_NUMBER 70

unsigned int gpio_irq;

int err;

// Signal handler used to detect button press
static irq_handler_t button_interrupt_handler(unsigned int irq, void *dev_id, struct pt_regs *regs) {
    printk("INTERRUPT TRIGGERED\n");

    struct siginfo info;
    
	if(task != NULL) { 
		memset(&info, 0, sizeof(info));
		info.si_signo = SIG_RUN;
		info.si_code = SI_QUEUE;

    /* Send the signal */
    err = send_sig_info(SIG_RUN, (struct kernel_siginfo *) &info, task);
    if(err < 0)
        printk("Error sending signal\n");
	}

    return (irq_handler_t) IRQ_HANDLED;
}

// Used to get process id of userspace script
static long int button_ioctl(struct file *file, unsigned cmd, unsigned long arg)
{
    // Get pid of task
    if(cmd == INIT_WATCHDOG) {
        task = get_current();
        printk("USERSPACE APP PID %d REGISTERED \n", task->pid);
    } else if (cmd == REM_WATCHDOG) {
        task = NULL;
        printk("USERSPACE APP DEREGISTERED \n");
    }
    return 0;
}

static int button_release(struct inode *device_file, struct file *instance) {
	if(task != NULL)
		task = NULL;
	return 0;
}

struct file_operations Fops = {
    .release = button_release,
	.unlocked_ioctl = button_ioctl,
};

static int __init button_detector_init(void) {
    printk(KERN_INFO "BUTTON DETECTOR KERNEL MODULE: INITILIASING\n");

    // Request GPIO pin and configure it as an input with pull-up resistor
    if (!gpio_is_valid(GPIO_NUMBER)) {+
        printk("BUTTON KERNEL MODULE: INVALID GPIO");
    }        
    
    // The return value is zero for success, else a negative errno.  
    err = gpio_request(GPIO_NUMBER, "button_gpio");
    if (err < 0) {
        printk(KERN_ERR "BUTTON DETECTOR KERNEL MODULE: GPIO REQUEST FAILED\n");
        return err;
    }

    // The return value is zero for success, else a negative errno.
    err = gpio_direction_input(GPIO_NUMBER);
    if (err < 0) {
        printk(KERN_ERR "BUTTON DETECTOR KERNEL MODULE: GPIO DIRECTION INPUT FAILED\n");
        return err;
    }   
    gpio_set_debounce(GPIO_NUMBER, 100); /* Adjust this number to sync with circut */

    // Request the IRQ for the button GPIO pin to setup interrupt
    gpio_irq = gpio_to_irq(GPIO_NUMBER);

    // The return value is zero for success, else a negative errno.
    err = request_irq(gpio_irq, (irq_handler_t) button_interrupt_handler, IRQF_TRIGGER_FALLING, "BUTTON_IRQ", NULL);
    if (err < 0) {
        printk(KERN_ERR "BUTTON DETECTOR KERNEL MODULE: IRQ REQUEST FAILED\n");
        gpio_free(GPIO_NUMBER);
        return err;
    }

    // The return value is zero for success, else a negative errno.
    err = register_chrdev(MAJOR_NUMBER, "BUTTON KERNEL MODULE IRQ SIGNAL", &Fops);
    if (err < 0){
        printk(KERN_ALERT "BUTTON DETECTOR KERNEL MODULE: FAILED TO REGISTER\n");
        gpio_free(GPIO_NUMBER);
        free_irq(gpio_irq, NULL);
        return err;
    }

    printk(KERN_INFO "BUTTON DETECTOR KERNEL MODULE: SUCCESSFULLY INITILIASED\n");
	printk("GPIO PIN IS MAPPED TO IRQ: %d\n", gpio_irq);

    return 0;
}

static void __exit button_detector_exit(void) {
    printk(KERN_INFO "BUTTON DETECTOR KERNEL MODULE: TERMINATING\n");
    // Free the GPIO, IRQ and CHRDEV resources
    free_irq(gpio_irq, NULL);
    gpio_free(GPIO_NUMBER);
    unregister_chrdev(MAJOR_NUMBER, "gpio_irq_signal");
    printk(KERN_INFO "BUTTON DETECTOR KERNEL MODULE: TERMINATED\n");
}

module_init(button_detector_init);
module_exit(button_detector_exit);