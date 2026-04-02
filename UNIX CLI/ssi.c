#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <pwd.h>
#include <sys/types.h>
#include <readline/readline.h>
#include <readline/history.h>

#define MAX_BG_JOBS 100
#define MAX_ARGS 64

typedef struct {
    pid_t pid;
    char cmd[512];   // store full command string
    int active;
} bg_job;

static bg_job bg_jobs[MAX_BG_JOBS];
static int bg_count = 0;

/* Simple tokenizer: returns pointer into input (input must remain valid) */
char** tokenize_input(char* input) {
    char** tokens = calloc(MAX_ARGS, sizeof(char*));
    if (!tokens) return NULL;
    int token_count = 0;
    char* saveptr = NULL;
    char* token = strtok_r(input, " \t\n", &saveptr);

    while (token != NULL && token_count < MAX_ARGS - 1) {
        tokens[token_count++] = token;
        token = strtok_r(NULL, " \t\n", &saveptr);
    }
    tokens[token_count] = NULL;
    return tokens;
}

/* Check background jobs for termination (non-blocking) and update list */
void handle_bg_jobs() {
    for (int i = 0; i < bg_count; i++) {
        if (bg_jobs[i].active) {
            int status;
            pid_t result = waitpid(bg_jobs[i].pid, &status, WNOHANG);
            if (result > 0) {
                printf("%d: %s has terminated.\n", bg_jobs[i].pid, bg_jobs[i].cmd);
                fflush(stdout);
                bg_jobs[i].active = 0;
            }
        }
    }

    /* compact array to remove inactive jobs */
    int new_count = 0;
    for (int i = 0; i < bg_count; i++) {
        if (bg_jobs[i].active) {
            if (i != new_count) bg_jobs[new_count] = bg_jobs[i];
            new_count++;
        }
    }
    bg_count = new_count;
}

void add_bg_job(pid_t pid, char** tokens) {
    if (bg_count >= MAX_BG_JOBS) {
        fprintf(stderr, "Max background jobs reached\n");
        return;
    }

    bg_jobs[bg_count].pid = pid;
    bg_jobs[bg_count].active = 1;

    /* Build a printable command string from tokens */
    bg_jobs[bg_count].cmd[0] = '\0';
    for (int i = 0; tokens[i] != NULL; i++) {
        strncat(bg_jobs[bg_count].cmd, tokens[i], sizeof(bg_jobs[bg_count].cmd) - strlen(bg_jobs[bg_count].cmd) - 1);
        if (tokens[i + 1] != NULL)
            strncat(bg_jobs[bg_count].cmd, " ", sizeof(bg_jobs[bg_count].cmd) - strlen(bg_jobs[bg_count].cmd) - 1);
    }

    bg_count++;
}

void list_bg_jobs() {
    int active = 0;
    for (int i = 0; i < bg_count; i++) {
        if (bg_jobs[i].active) {
            printf("%d: %s\n", bg_jobs[i].pid, bg_jobs[i].cmd);
            active++;
        }
    }
    printf("Total Background jobs: %d\n", active);
}

/* SIGINT handler for the shell (Ctrl-C) */
void sigint_handler(int sig) {
    (void)sig;
    /* Print a newline and redisplay prompt when using readline */
    printf("\n");
    rl_on_new_line();
    rl_replace_line("", 0);
    rl_redisplay();
}

int main(void) {
    char* input = NULL;
    char hostname[256];
    char cwd[1024];

    /* Install SIGINT handler for the shell */
    if (signal(SIGINT, sigint_handler) == SIG_ERR) {
        perror("signal");
        exit(EXIT_FAILURE);
    }

    while (1) {
        /* Reap/announce background jobs */
        handle_bg_jobs();

        /* Build prompt */
        if (getcwd(cwd, sizeof(cwd)) == NULL) {
            strncpy(cwd, "?", sizeof(cwd) - 1);
            cwd[sizeof(cwd) - 1] = '\0';
        }

        if (gethostname(hostname, sizeof(hostname)) != 0) {
            strncpy(hostname, "host", sizeof(hostname) - 1);
            hostname[sizeof(hostname) - 1] = '\0';
        }

        char* username = getlogin();
        if (username == NULL) {
            struct passwd* pw = getpwuid(getuid());
            if (pw) username = pw->pw_name;
            else username = "user";
        }

        char prompt[2048];
        snprintf(prompt, sizeof(prompt), "%s@%s: %s > ", username, hostname, cwd);

        input = readline(prompt);

        if (input == NULL) {
            /* EOF (Ctrl-D) at empty prompt -> exit shell */
            printf("\n");
            break;
        }

        if (strlen(input) == 0) {
            free(input);
            continue;
        }

        add_history(input);

        /* Duplicate input so tokenizer can modify it */
        char* input_copy = strdup(input);
        if (!input_copy) {
            perror("strdup");
            free(input);
            continue;
        }

        char** tokens = tokenize_input(input_copy);
        if (!tokens) {
            free(input_copy);
            free(input);
            continue;
        }

        if (tokens[0] == NULL) {
            free(tokens);
            free(input_copy);
            free(input);
            continue;
        }

        /* Built-ins */

        if (strcmp(tokens[0], "cd") == 0) {
            /* cd takes zero or one argument; ignore extra args */
            char* target = tokens[1];
            if (target == NULL || strcmp(target, "~") == 0) {
                char* home = getenv("HOME");
                if (home) {
                    if (chdir(home) != 0) perror("chdir");
                } else {
                    fprintf(stderr, "HOME not set\n");
                }
            } else {
                if (chdir(target) != 0) {
                    printf("cd: %s: No such file or directory\n", target);
                }
            }
            free(tokens);
            free(input_copy);
            free(input);
            continue;
        }

        if (strcmp(tokens[0], "bglist") == 0) {
            list_bg_jobs();
            free(tokens);
            free(input_copy);
            free(input);
            continue;
        }

        int is_bg = 0;
        if (strcmp(tokens[0], "bg") == 0) {
            is_bg = 1;
            /* shift tokens left by one */
            for (int i = 0; tokens[i] != NULL; i++) {
                tokens[i] = tokens[i + 1];
            }
            if (tokens[0] == NULL) {
                /* nothing after bg */
                free(tokens);
                free(input_copy);
                free(input);
                continue;
            }
        }

        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            free(tokens);
            free(input_copy);
            free(input);
            continue;
        }

        if (pid == 0) {
    // --- Child process ---
            signal(SIGINT, SIG_DFL);
            execvp(tokens[0], tokens);
            printf("%s: No such file or directory\n", tokens[0]);
            _exit(127);
        } else {
            // --- Parent process ---
            if (is_bg) {
                // Build full command string before freeing anything
                char cmd_buf[512] = "";
                for (int i = 0; tokens[i] != NULL; i++) {
                    strncat(cmd_buf, tokens[i], sizeof(cmd_buf) - strlen(cmd_buf) - 1);
                    if (tokens[i + 1] != NULL)
                        strncat(cmd_buf, " ", sizeof(cmd_buf) - strlen(cmd_buf) - 1);
                }

                add_bg_job(pid, tokens);   // track job safely
                printf("Started background job %d: %s\n", pid, cmd_buf);
                fflush(stdout);            // ensure prompt appears right away
            } else {
                int status;
                waitpid(pid, &status, 0);  // foreground job, block until done
            }
        }

        free(tokens);
        free(input_copy);
        free(input);
    }

    return 0;
}
