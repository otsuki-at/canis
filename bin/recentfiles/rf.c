#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<fnmatch.h>
#include<unistd.h>
#include<time.h>

char *EventList[5];
int EventCount = 0;
int Days = 0;
char *LogFile = NULL;
// char *Glob = NULL;

int print_usage(){
    char *usage = "Usage: recentfiles EXTENSION...\n"
                  "       EXTENSION is .txt or .tex for exmaple.\n";

    printf("%s", usage);
    return 0;
}

int ematch(char *event){
    for(int i=0; i<EventCount; i++){
        if(strcmp(EventList[i], event)==0){
            return 0;
        }
    }
    return 1;
}

int winndays(char *date, int days){
    if(days == 0){
        return 0;
    }

    time_t t_current_time;
    time(&t_current_time);
    time_t t_days_ago = t_current_time - (days * 24 * 60 * 60);

    struct tm tm_date;
    int year, month, day, hour, min, sec, msec;
    if(sscanf(date, "%d-%d-%dT%d:%d:%d.%d", &year, &month, &day, &hour, &min, &sec, &msec) != 7){
        printf("日付の解析に失敗しました\n");
        return 1;
    }
    tm_date.tm_year = year - 1900;
    tm_date.tm_mon = month -1;
    tm_date.tm_mday = day;
    tm_date.tm_hour = hour;
    tm_date.tm_min = min;
    tm_date.tm_sec = sec;
    tm_date.tm_isdst = -1;
    time_t t_date = mktime(&tm_date);

    if(t_days_ago < t_date){
        return 0;
    }else{
        return 1;
    }

    return 1;
}

int print_paths(char *glob){
    FILE *fp;
    // need to replace with flex representation.
    // char *file_name = "/home/mukohara/git/trigora/log/converted.log";
    char date[64];
    char inode[32];
    char event[32];
    char path[256];

    fp = fopen(LogFile, "r");
    if (fp == NULL){
        printf("Cannot open %s\n", LogFile);
        return 1;
    }

    while(fscanf(fp, "%[^,],%[^,],%[^,],%s\n", date, inode, event, path) != EOF){
        if ((path != NULL)&&(fnmatch(glob, path, 0)==0)&&(ematch(event)==0)&&(winndays(date, Days)==0)){
            printf("%s\n", path);
        }
    }

    fclose(fp);
    return 0;
}

int main(int argc, char *argv[]){
    int opt;

    // if (argc < 2){
    //     printf("Error: Too few arguments.\n");
    //     print_usage();
    // }

    opterr = 0;

    while((opt = getopt(argc, argv, "t:n:f:h")) != -1){
        switch(opt){
            case 't':
                // printf("-t detected\n");
                // printf("arg is %s\n", optarg);
                EventList[EventCount] = optarg;
                EventCount++;
                break;
            case 'n':
                // printf("-n detected\n");
                // printf("arg is %s\n", optarg);
                Days = atoi(optarg);
                break;
            case 'f':
                // printf("-f detected\n");
                // printf("arg is %s\n", optarg);
                LogFile = optarg;
                break;
            case 'p':
                printf("-p option is not implemented now.\n");
                break;
            case 'h':
                print_usage();
                break;

            default:
                print_usage();
                break;
        }
    }

    print_paths(argv[optind]);

    return 0;
}
