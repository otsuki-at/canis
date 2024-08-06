#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define MAX_LEN 1024
#define pr printf("1\n")

struct hashinfo {
    char time[27];
    char hash[65];
    char path[MAX_LEN];
} latest;

struct hashinfo split_info(char *line){
    struct hashinfo info;
    strcpy(info.time, strtok(line, ","));
    strcpy(info.hash, strtok(NULL, ","));
    strcpy(info.path, strtok(NULL, ","));
    return info;
}

int search_hash(FILE *fp, char *file){
    char line[MAX_LEN];
    struct hashinfo info;
    int cnt = 0;
    while(fgets(line, MAX_LEN, fp) != NULL){
        info = split_info(line);

        if (strcmp(info.path, file) == 0){
            latest = info;
            cnt++;
        }
    }
    return cnt;
}

int main(int argc, char *argv[]){
    FILE *fp;
    int cnt;
    char filepath[MAX_LEN];
    char logdir[256];
    char *logenv = getenv("LOGDIR");

    if (logenv != NULL){
        strcpy(logdir, logenv);
        strcat(logdir, "/hash.log");
    }
    else{
        return 1;
    }

    fp = fopen(logdir, "r");
    if(fp == NULL){
        fprintf(stderr, "%s\n", strerror(errno));
        return 1;
    }

    strcpy(filepath,argv[1]);

    strcat(filepath, "\n");
    cnt = search_hash(fp, filepath);

    if(cnt){
        printf("%s,%s%s\n", latest.time, latest.path, latest.hash);
    }
    else{
        printf("%s is not found\n",argv[1]);
    }
}
