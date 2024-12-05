/*
  FUSE: Filesystem in Userspace
  Copyright (C) 2001-2007  Miklos Szeredi <miklos@szeredi.hu>
  Copyright (C) 2011       Sebastian Pipping <sebastian@pipping.org>

  This program can be distributed under the terms of the GNU GPLv2.
  See the file COPYING.
*/

/** @file
 *
 * This file system mirrors the existing file system hierarchy of the
 * system, starting at the root file system. This is implemented by
 * just "passing through" all requests to the corresponding user-space
 * libc functions. Its performance is terrible.
 *
 * Compile with
 *
 *     gcc -Wall redis-collector.c `pkg-config fuse3 --cflags --libs` -o redis-collector -lhiredis
 *
 * ## Source code ##
 * \include passthrough.c
 */


#define FUSE_USE_VERSION 31

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#define _GNU_SOURCE

#ifdef linux
/* For pread()/pwrite()/utimensat() */
#define _XOPEN_SOURCE 700
#endif

#include <fuse.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#ifdef __FreeBSD__
#include <sys/socket.h>
#include <sys/un.h>
#endif
#include <sys/time.h>
#ifdef HAVE_SETXATTR
#include <sys/xattr.h>
#endif
#include <hiredis/hiredis.h>

#include "collector_helpers.h"
#define MAX_ARG_NUM 100

static int fill_dir_plus = 0;
char ignore_path[MAX_ARG_NUM][200];
redisContext *c;
redisReply *rep;

// ログに出力しないファイルのパスの設定
void set_ignore(){
    int i=0;
    char ignore[10];
    sprintf(ignore,"IGNORE%d",i);
    while(getenv(ignore)!=NULL){
        strcpy(ignore_path[i],getenv(ignore));
        i++;
        sprintf(ignore,"IGNORE%d",i);
    }
}

char* replace(char* s, const char* before, const char* after)
{
	const size_t before_len = strlen(before);
	if (before_len == 0){
		return s;
	}

	const size_t after_len = strlen(after);
	char* p = s;

	for (;;){
		// 置換対象の文字列を探す
		p = strstr(p, before);
		if (p == NULL){
			break;
		}

		*p = '\0';

        strcat(s, after);
        char *path_before = (char*)malloc(strlen(p+before_len)+1);
        memcpy(path_before,p+before_len,strlen(p+before_len)+1);
        strcat(s, path_before);

		// 探索開始位置をずらす
		p += after_len;
	}
	return s;
}

void publish_log(char *func_name, const char *path1, const char *path2)
{
        struct timeval myTime;
        struct stat stat_buf;
        char date[64];
		int found = 0;
        int len = sizeof(ignore_path)/sizeof(ignore_path[0]);

        char *user = getenv("USERNAME");
        char usercan[256];
        if (user != NULL){
            strcpy(usercan, user);
            strcat(usercan, ".can");
        }

		char* p1 = (char*)malloc(strlen(path1)+1);
		memcpy(p1, path1, strlen(path1)+1);
		char* p2 = (char*)malloc(strlen(path2)+1); 
		memcpy(p2, path2, strlen(path2)+1);

        stat(path1, &stat_buf);
        gettimeofday(&myTime, NULL);
        strftime(date, sizeof(date), "%Y-%m-%dT%H:%M:%S", localtime(&myTime.tv_sec));

		for(int i = 0; i < len; i++){
		    if(path1 != NULL && strcmp(ignore_path[i], path1) == 0){
                found = 1;
				break;
	    	}
		}

        // Redisに操作時間，操作，パスを出力
        if(strcmp(path2, "null")==0 && found==0){
			replace(p1, usercan, user);
            rep = (redisReply *)redisCommand(c,"publish fuse-watch-log %s.%06ld,%ld,%s,%s",date, myTime.tv_usec, stat_buf.st_ino, func_name, p1);
            // fprintf(stdout, "%s.%06ld,%ld,%s,%s\n", date, myTime.tv_usec, stat_buf.st_ino, func_name, path1);
            if( NULL == rep ){
                redisFree( c );
                exit(-1);
            }
            if( REDIS_REPLY_ERROR == rep->type ){
                redisFree( c );
                freeReplyObject( rep );
                exit(-1);
            }
        }else if(found==0){
			replace(p1, usercan, user);
			replace(p2, usercan, user);
            rep = (redisReply *)redisCommand(c, "publish fuse-watch-log %s.%06ld,%ld,%s,%s,%s", date, myTime.tv_usec, stat_buf.st_ino, func_name, p1, p2);
        //     fprintf(stdout, "%s.%06ld,%ld,%s,%s,%s\n", date, myTime.tv_usec, stat_buf.st_ino, func_name, path1, path2);
            if( NULL == rep ){
                redisFree( c );
                exit(-1);
            }
            if( REDIS_REPLY_ERROR == rep->type ){
                redisFree( c );
                freeReplyObject( rep );
                exit(-1);
            }
        }
        freeReplyObject( rep );
		free(p1);
		free(p2);
}

static void *xmp_init(struct fuse_conn_info *conn,
		      struct fuse_config *cfg)
{
    publish_log("init", "null", "null");
	(void) conn;
	cfg->use_ino = 1;

	/* Pick up changes from lower filesystem right away. This is
	   also necessary for better hardlink support. When the kernel
	   calls the unlink() handler, it does not know the inode of
	   the to-be-removed entry and can therefore not invalidate
	   the cache of the associated inode - resulting in an
	   incorrect st_nlink value being reported for any remaining
	   hardlinks to this inode. */
	cfg->entry_timeout = 0;
	cfg->attr_timeout = 0;
	cfg->negative_timeout = 0;

	return NULL;
}

static int xmp_getattr(const char *path, struct stat *stbuf,
		       struct fuse_file_info *fi)
{
    publish_log("getattr", path, "null");
	(void) fi;
	int res;

	res = lstat(path, stbuf);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_access(const char *path, int mask)
{
    publish_log("access", path, "null");
	int res;

	res = access(path, mask);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_readlink(const char *path, char *buf, size_t size)
{
    publish_log("readlink", path, "null");
	int res;

	res = readlink(path, buf, size - 1);
	if (res == -1)
		return -errno;

	buf[res] = '\0';
	return 0;
}


static int xmp_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
		       off_t offset, struct fuse_file_info *fi,
		       enum fuse_readdir_flags flags)
{
    publish_log("readdir", path, "null");
	DIR *dp;
	struct dirent *de;

	(void) offset;
	(void) fi;
	(void) flags;

	dp = opendir(path);
	if (dp == NULL)
		return -errno;

	while ((de = readdir(dp)) != NULL) {
		struct stat st;
		memset(&st, 0, sizeof(st));
		st.st_ino = de->d_ino;
		st.st_mode = de->d_type << 12;
		if (filler(buf, de->d_name, &st, 0, fill_dir_plus))
			break;
	}

	closedir(dp);
	return 0;
}

static int xmp_mknod(const char *path, mode_t mode, dev_t rdev)
{
    publish_log("mknod", path, "null");
	int res;

	res = mknod_wrapper(AT_FDCWD, path, NULL, mode, rdev);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_mkdir(const char *path, mode_t mode)
{
    publish_log("mkdir", path, "null");
	int res;

	res = mkdir(path, mode);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_unlink(const char *path)
{
    publish_log("unlink", path, "null");
	int res;

	res = unlink(path);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_rmdir(const char *path)
{
    publish_log("rmdir", path, "null");
	int res;

	res = rmdir(path);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_symlink(const char *from, const char *to)
{
    publish_log("symlink", from, to);
	int res;

	res = symlink(from, to);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_rename(const char *from, const char *to, unsigned int flags)
{
    publish_log("rename", from, to);
	int res;

	if (flags)
		return -EINVAL;

	res = rename(from, to);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_link(const char *from, const char *to)
{
    publish_log("link", from, to);
	int res;

	res = link(from, to);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_chmod(const char *path, mode_t mode,
		     struct fuse_file_info *fi)
{
    publish_log("chmod", path, "null");
	(void) fi;
	int res;

	res = chmod(path, mode);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_chown(const char *path, uid_t uid, gid_t gid,
		     struct fuse_file_info *fi)
{
    publish_log("chown", path, "null");
	(void) fi;
	int res;

	res = lchown(path, uid, gid);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_truncate(const char *path, off_t size,
			struct fuse_file_info *fi)
{
    publish_log("truncate", path, "null");
	int res;

	if (fi != NULL)
		res = ftruncate(fi->fh, size);
	else
		res = truncate(path, size);
	if (res == -1)
		return -errno;

	return 0;
}

#ifdef HAVE_UTIMENSAT
static int xmp_utimens(const char *path, const struct timespec ts[2],
		       struct fuse_file_info *fi)
{
    publish_log("utimens", path , "null");
	(void) fi;
	int res;

	/* don't use utime/utimes since they follow symlinks */
	res = utimensat(0, path, ts, AT_SYMLINK_NOFOLLOW);
	if (res == -1)
		return -errno;

	return 0;
}
#endif

static int xmp_create(const char *path, mode_t mode,
		      struct fuse_file_info *fi)
{
    publish_log("create", path, "null");
	int res;

	res = open(path, fi->flags, mode);
	if (res == -1)
		return -errno;

	fi->fh = res;
	return 0;
}

static int xmp_open(const char *path, struct fuse_file_info *fi)
{
    publish_log("open", path, "null");
	int res;

	res = open(path, fi->flags);
	if (res == -1)
		return -errno;

	fi->fh = res;
	return 0;
}

static int xmp_read(const char *path, char *buf, size_t size, off_t offset,
		    struct fuse_file_info *fi)
{
    publish_log("read", path, "null");
	int fd;
	int res;

	if(fi == NULL)
		fd = open(path, O_RDONLY);
	else
		fd = fi->fh;

	if (fd == -1)
		return -errno;

	res = pread(fd, buf, size, offset);
	if (res == -1)
		res = -errno;

	if(fi == NULL)
		close(fd);
	return res;
}

static int xmp_write(const char *path, const char *buf, size_t size,
		     off_t offset, struct fuse_file_info *fi)
{
    publish_log("write", path, "null");
	int fd;
	int res;

	(void) fi;
	if(fi == NULL)
		fd = open(path, O_WRONLY);
	else
		fd = fi->fh;

	if (fd == -1)
		return -errno;

	res = pwrite(fd, buf, size, offset);
	if (res == -1)
		res = -errno;

	if(fi == NULL)
		close(fd);
	return res;
}

static int xmp_statfs(const char *path, struct statvfs *stbuf)
{
    publish_log("statfs", path, "null");
	int res;

	res = statvfs(path, stbuf);
	if (res == -1)
		return -errno;

	return 0;
}

static int xmp_release(const char *path, struct fuse_file_info *fi)
{
    publish_log("release", path, "null");
	(void) path;
	close(fi->fh);
	return 0;
}

static int xmp_fsync(const char *path, int isdatasync,
		     struct fuse_file_info *fi)
{
    publish_log("fsync", path, "null");
	/* Just a stub.	 This method is optional and can safely be left
	   unimplemented */

	(void) path;
	(void) isdatasync;
	(void) fi;
	return 0;
}

#ifdef HAVE_POSIX_FALLOCATE
static int xmp_fallocate(const char *path, int mode,
			off_t offset, off_t length, struct fuse_file_info *fi)
{
    publish_log("fallocate", path, "null");
	int fd;
	int res;

	(void) fi;

	if (mode)
		return -EOPNOTSUPP;

	if(fi == NULL)
		fd = open(path, O_WRONLY);
	else
		fd = fi->fh;
	if (fd == -1)

		return -errno;

	res = -posix_fallocate(fd, offset, length);

	if(fi == NULL)
		close(fd);
	return res;
}
#endif

#ifdef HAVE_SETXATTR
/* xattr operations are optional and can safely be left unimplemented */
static int xmp_setxattr(const char *path, const char *name, const char *value,
			size_t size, int flags)
{
    publish_log("setxattr", path, "null");
	int res = lsetxattr(path, name, value, size, flags);
	if (res == -1)
		return -errno;
	return 0;
}

static int xmp_getxattr(const char *path, const char *name, char *value,
			size_t size)
{
    publish_log("getxattr", path, "null");
	int res = lgetxattr(path, name, value, size);
	if (res == -1)
		return -errno;
	return res;
}

static int xmp_listxattr(const char *path, char *list, size_t size)
{
    publish_log("listxattr", path, "null");
	int res = llistxattr(path, list, size);
	if (res == -1)
		return -errno;
	return res;
}

static int xmp_removexattr(const char *path, const char *name)
{
    publish_log("removexattr", path, "null");
	int res = lremovexattr(path, name);
	if (res == -1)
		return -errno;
	return 0;
}
#endif /* HAVE_SETXATTR */

#ifdef HAVE_COPY_FILE_RANGE
static ssize_t xmp_copy_file_range(const char *path_in,
				   struct fuse_file_info *fi_in,
				   off_t offset_in, const char *path_out,
				   struct fuse_file_info *fi_out,
				   off_t offset_out, size_t len, int flags)
{
    publish_log("copy_file_range", path_in, path_out);
	int fd_in, fd_out;
	ssize_t res;

	if(fi_in == NULL)
		fd_in = open(path_in, O_RDONLY);
	else
		fd_in = fi_in->fh;

	if (fd_in == -1)
		return -errno;

	if(fi_out == NULL)
		fd_out = open(path_out, O_WRONLY);
	else
		fd_out = fi_out->fh;

	if (fd_out == -1) {
		close(fd_in);
		return -errno;
	}

	res = copy_file_range(fd_in, &offset_in, fd_out, &offset_out, len,
			      flags);
	if (res == -1)
		res = -errno;

	if (fi_out == NULL)
		close(fd_out);
	if (fi_in == NULL)
		close(fd_in);

	return res;
}
#endif

static off_t xmp_lseek(const char *path, off_t off, int whence, struct fuse_file_info *fi)
{
    publish_log("lseek", path, "null");
	int fd;
	off_t res;

	if (fi == NULL)
		fd = open(path, O_RDONLY);
	else
		fd = fi->fh;

	if (fd == -1)
		return -errno;

	res = lseek(fd, off, whence);
	if (res == -1)
		res = -errno;

	if (fi == NULL)
		close(fd);
	return res;
}

static const struct fuse_operations xmp_oper = {
	.init           = xmp_init,
	.getattr	= xmp_getattr,
	.access		= xmp_access,
	.readlink	= xmp_readlink,
	.readdir	= xmp_readdir,
	.mknod		= xmp_mknod,
	.mkdir		= xmp_mkdir,
	.symlink	= xmp_symlink,
	.unlink		= xmp_unlink,
	.rmdir		= xmp_rmdir,
	.rename		= xmp_rename,
	.link		= xmp_link,
	.chmod		= xmp_chmod,
	.chown		= xmp_chown,
	.truncate	= xmp_truncate,
#ifdef HAVE_UTIMENSAT
	.utimens	= xmp_utimens,
#endif
	.open		= xmp_open,
	.create 	= xmp_create,
	.read		= xmp_read,
	.write		= xmp_write,
	.statfs		= xmp_statfs,
	.release	= xmp_release,
	.fsync		= xmp_fsync,
#ifdef HAVE_POSIX_FALLOCATE
	.fallocate	= xmp_fallocate,
#endif
#ifdef HAVE_SETXATTR
	.setxattr	= xmp_setxattr,
	.getxattr	= xmp_getxattr,
	.listxattr	= xmp_listxattr,
	.removexattr	= xmp_removexattr,
#endif
#ifdef HAVE_COPY_FILE_RANGE
	.copy_file_range = xmp_copy_file_range,
#endif
	.lseek		= xmp_lseek,
};

int main(int argc, char *argv[])
{
    // Redisに接続
    c = redisConnect("127.0.0.1", 6379);

    if (c == NULL || c->err) {
        if (c) {
            printf("Error: %s\n", c->errstr);
            redisFree(c);
        } else {
            printf("Can't allocate redis context\n");
        }
        return 1;
    }

	enum { MAX_ARGS = 10 };
	int i, ret, new_argc;
	char *new_argv[MAX_ARGS];

    set_ignore();

	umask(0);
			/* Process the "--plus" option apart */
	for (i=0, new_argc=0; (i<argc) && (new_argc<MAX_ARGS); i++) {
		if (!strcmp(argv[i], "--plus")) {
			fill_dir_plus = FUSE_FILL_DIR_PLUS;
		} else {
			new_argv[new_argc++] = argv[i];
		}
	}
	ret = fuse_main(new_argc, new_argv, &xmp_oper, NULL);
    redisFree(c);
    return ret;
}
