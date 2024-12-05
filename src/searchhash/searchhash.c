#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define MAX_LEN 1024

struct hashinfo {
    char time[27];
    char hash[65];
    char path[MAX_LEN];
} latest;

// ログファイルの行を分割
struct hashinfo split_info(char *line){
    struct hashinfo info;
    strcpy(info.time, strtok(line, ","));
    strcpy(info.hash, strtok(NULL, ","));
    strcpy(info.path, strtok(NULL, ","));
    return info;
}

// 探したいファイルのハッシュを探索
int search_hash(FILE *fp, char *hash){
    char line[MAX_LEN];
    struct hashinfo info;
    int cnt = 0;
    while(fgets(line, MAX_LEN, fp) != NULL){
        info = split_info(line);

        if (strcmp(info.hash, hash) == 0){
            latest = info;
            return ++cnt;
        }
    }
    return cnt;
}

int main(int argc, char *argv[]){
    FILE *fp;
    int cnt;
    char arghash[65];
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

    strcpy(arghash,argv[1]);

    cnt = search_hash(fp, arghash);

    if(cnt){
        // 引数のファイルの作成時間，パスおよびハッシュ値を表示
        printf("操作された時刻: %s\nハッシュ値: %s\nファイルパス: %s", latest.time, latest.hash, latest.path);
    }
    else{
        // 引数のファイルが見つからなかった場合の処理
        printf("%s is not found\n",argv[1]);
    }
    fclose(fp);
}
