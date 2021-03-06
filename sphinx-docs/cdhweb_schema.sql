-- MySQL dump 10.13  Distrib 5.7.17, for osx10.12 (x86_64)
--
-- Host: localhost    Database: cdhweb
-- ------------------------------------------------------
-- Server version	5.7.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_blogpost`
--

DROP TABLE IF EXISTS `blog_blogpost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_blogpost` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords_string` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) DEFAULT NULL,
  `_meta_title` varchar(500) DEFAULT NULL,
  `description` longtext NOT NULL,
  `gen_description` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `short_url` varchar(200) DEFAULT NULL,
  `in_sitemap` tinyint(1) NOT NULL,
  `content` longtext NOT NULL,
  `featured_image` varchar(255) DEFAULT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `blog_blogpost_site_id_7995688f_fk_django_site_id` (`site_id`),
  KEY `blog_blogpost_publish_date_703abc16` (`publish_date`),
  CONSTRAINT `blog_blogpost_site_id_7995688f_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_blogpost_attachments`
--

DROP TABLE IF EXISTS `blog_blogpost_attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_blogpost_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `blogpost_id` int(11) NOT NULL,
  `attachment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `blog_blogpost_attachment_blogpost_id_attachment_i_e8a38ffa_uniq` (`blogpost_id`,`attachment_id`),
  KEY `blog_blogpost_attach_attachment_id_5a72eaa8_fk_resources` (`attachment_id`),
  CONSTRAINT `blog_blogpost_attach_attachment_id_5a72eaa8_fk_resources` FOREIGN KEY (`attachment_id`) REFERENCES `resources_attachment` (`id`),
  CONSTRAINT `blog_blogpost_attach_blogpost_id_540f9217_fk_blog_blog` FOREIGN KEY (`blogpost_id`) REFERENCES `blog_blogpost` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_blogpost_related_posts`
--

DROP TABLE IF EXISTS `blog_blogpost_related_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_blogpost_related_posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_blogpost_id` int(11) NOT NULL,
  `to_blogpost_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `blog_blogpost_related_po_from_blogpost_id_to_blog_3bd0f49f_uniq` (`from_blogpost_id`,`to_blogpost_id`),
  KEY `blog_blogpost_relate_to_blogpost_id_35f7acdd_fk_blog_blog` (`to_blogpost_id`),
  CONSTRAINT `blog_blogpost_relate_from_blogpost_id_27ea4c18_fk_blog_blog` FOREIGN KEY (`from_blogpost_id`) REFERENCES `blog_blogpost` (`id`),
  CONSTRAINT `blog_blogpost_relate_to_blogpost_id_35f7acdd_fk_blog_blog` FOREIGN KEY (`to_blogpost_id`) REFERENCES `blog_blogpost` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_blogpost_users`
--

DROP TABLE IF EXISTS `blog_blogpost_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_blogpost_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `blogpost_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `blog_blogpost_users_blogpost_id_person_id_ff67fa37_uniq` (`blogpost_id`,`person_id`),
  KEY `blog_blogpost_users_person_id_ff7f0f6d_fk_auth_user_id` (`person_id`),
  CONSTRAINT `blog_blogpost_users_blogpost_id_58e9434b_fk_blog_blogpost_id` FOREIGN KEY (`blogpost_id`) REFERENCES `blog_blogpost` (`id`),
  CONSTRAINT `blog_blogpost_users_person_id_ff7f0f6d_fk_auth_user_id` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `conf_setting`
--

DROP TABLE IF EXISTS `conf_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conf_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `value` varchar(2000) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `conf_setting_site_id_b235f7ed_fk_django_site_id` (`site_id`),
  CONSTRAINT `conf_setting_site_id_b235f7ed_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `core_sitepermission`
--

DROP TABLE IF EXISTS `core_sitepermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_sitepermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `core_sitepermission_user_id_0a3cbb11_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `core_sitepermission_sites`
--

DROP TABLE IF EXISTS `core_sitepermission_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_sitepermission_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sitepermission_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_sitepermission_site_sitepermission_id_site_i_e3e7353a_uniq` (`sitepermission_id`,`site_id`),
  KEY `core_sitepermission_sites_site_id_38038b76_fk_django_site_id` (`site_id`),
  CONSTRAINT `core_sitepermission__sitepermission_id_d33bc79e_fk_core_site` FOREIGN KEY (`sitepermission_id`) REFERENCES `core_sitepermission` (`id`),
  CONSTRAINT `core_sitepermission_sites_site_id_38038b76_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_cas_ng_proxygrantingticket`
--

DROP TABLE IF EXISTS `django_cas_ng_proxygrantingticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_cas_ng_proxygrantingticket` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_key` varchar(255) DEFAULT NULL,
  `pgtiou` varchar(255) DEFAULT NULL,
  `pgt` varchar(255) DEFAULT NULL,
  `date` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_cas_ng_proxygrant_session_key_user_id_4cd2ea19_uniq` (`session_key`,`user_id`),
  KEY `django_cas_ng_proxyg_user_id_f833edd2_fk_auth_user` (`user_id`),
  CONSTRAINT `django_cas_ng_proxyg_user_id_f833edd2_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_cas_ng_sessionticket`
--

DROP TABLE IF EXISTS `django_cas_ng_sessionticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_cas_ng_sessionticket` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_key` varchar(255) NOT NULL,
  `ticket` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_comment_flags`
--

DROP TABLE IF EXISTS `django_comment_flags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_comment_flags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` varchar(30) NOT NULL,
  `flag_date` datetime(6) NOT NULL,
  `comment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_comment_flags_user_id_comment_id_flag_537f77a7_uniq` (`user_id`,`comment_id`,`flag`),
  KEY `django_comment_flags_comment_id_d8054933_fk_django_comments_id` (`comment_id`),
  KEY `django_comment_flags_flag_8b141fcb` (`flag`),
  CONSTRAINT `django_comment_flags_comment_id_d8054933_fk_django_comments_id` FOREIGN KEY (`comment_id`) REFERENCES `django_comments` (`id`),
  CONSTRAINT `django_comment_flags_user_id_f3f81f0a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_comments`
--

DROP TABLE IF EXISTS `django_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_pk` longtext NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_email` varchar(254) NOT NULL,
  `user_url` varchar(200) NOT NULL,
  `comment` longtext NOT NULL,
  `submit_date` datetime(6) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `is_public` tinyint(1) NOT NULL,
  `is_removed` tinyint(1) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `django_comments_content_type_id_c4afe962_fk_django_co` (`content_type_id`),
  KEY `django_comments_site_id_9dcf666e_fk_django_site_id` (`site_id`),
  KEY `django_comments_user_id_a0a440a1_fk_auth_user_id` (`user_id`),
  KEY `django_comments_submit_date_514ed2d9` (`submit_date`),
  CONSTRAINT `django_comments_content_type_id_c4afe962_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_comments_site_id_9dcf666e_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`),
  CONSTRAINT `django_comments_user_id_a0a440a1_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_redirect`
--

DROP TABLE IF EXISTS `django_redirect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_redirect` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `old_path` varchar(200) NOT NULL,
  `new_path` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_redirect_site_id_old_path_ac5dd16b_uniq` (`site_id`,`old_path`),
  KEY `django_redirect_old_path_c6cc94d3` (`old_path`),
  CONSTRAINT `django_redirect_site_id_c3e37341_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events_event`
--

DROP TABLE IF EXISTS `events_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords_string` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) DEFAULT NULL,
  `_meta_title` varchar(500) DEFAULT NULL,
  `description` longtext NOT NULL,
  `gen_description` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `short_url` varchar(200) DEFAULT NULL,
  `in_sitemap` tinyint(1) NOT NULL,
  `content` longtext NOT NULL,
  `sponsor` varchar(80) DEFAULT NULL,
  `start_time` datetime(6) NOT NULL,
  `end_time` datetime(6) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `thumb` varchar(255) DEFAULT NULL,
  `event_type_id` int(11) NOT NULL,
  `location_id` int(11) DEFAULT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `events_event_publish_date_09a8edaf` (`publish_date`),
  KEY `events_event_event_type_id_000b97e2_fk_events_eventtype_id` (`event_type_id`),
  KEY `events_event_location_id_2fb4171f_fk_events_location_id` (`location_id`),
  KEY `events_event_site_id_d76095e0_fk_django_site_id` (`site_id`),
  CONSTRAINT `events_event_event_type_id_000b97e2_fk_events_eventtype_id` FOREIGN KEY (`event_type_id`) REFERENCES `events_eventtype` (`id`),
  CONSTRAINT `events_event_location_id_2fb4171f_fk_events_location_id` FOREIGN KEY (`location_id`) REFERENCES `events_location` (`id`),
  CONSTRAINT `events_event_site_id_d76095e0_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events_event_attachments`
--

DROP TABLE IF EXISTS `events_event_attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_event_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `attachment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `events_event_attachments_event_id_attachment_id_3d9f4104_uniq` (`event_id`,`attachment_id`),
  KEY `events_event_attachm_attachment_id_a982323a_fk_resources` (`attachment_id`),
  CONSTRAINT `events_event_attachm_attachment_id_a982323a_fk_resources` FOREIGN KEY (`attachment_id`) REFERENCES `resources_attachment` (`id`),
  CONSTRAINT `events_event_attachments_event_id_9c076439_fk_events_event_id` FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events_event_speakers`
--

DROP TABLE IF EXISTS `events_event_speakers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_event_speakers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `events_event_speakers_event_id_person_id_9ad2ecd3_uniq` (`event_id`,`person_id`),
  KEY `events_event_speakers_person_id_6ed24d8d_fk_auth_user_id` (`person_id`),
  CONSTRAINT `events_event_speakers_event_id_aa580a97_fk_events_event_id` FOREIGN KEY (`event_id`) REFERENCES `events_event` (`id`),
  CONSTRAINT `events_event_speakers_person_id_6ed24d8d_fk_auth_user_id` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events_eventtype`
--

DROP TABLE IF EXISTS `events_eventtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_eventtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events_location`
--

DROP TABLE IF EXISTS `events_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events_location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `short_name` varchar(80) NOT NULL,
  `address` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `generic_assignedkeyword`
--

DROP TABLE IF EXISTS `generic_assignedkeyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `generic_assignedkeyword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_order` int(11) DEFAULT NULL,
  `object_pk` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `keyword_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `generic_assignedkeyw_content_type_id_3dd89a7f_fk_django_co` (`content_type_id`),
  KEY `generic_assignedkeyw_keyword_id_44c17f9d_fk_generic_k` (`keyword_id`),
  CONSTRAINT `generic_assignedkeyw_content_type_id_3dd89a7f_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `generic_assignedkeyw_keyword_id_44c17f9d_fk_generic_k` FOREIGN KEY (`keyword_id`) REFERENCES `generic_keyword` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `generic_keyword`
--

DROP TABLE IF EXISTS `generic_keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `generic_keyword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `generic_keyword_site_id_c5be0acc_fk_django_site_id` (`site_id`),
  CONSTRAINT `generic_keyword_site_id_c5be0acc_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `generic_rating`
--

DROP TABLE IF EXISTS `generic_rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `generic_rating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` int(11) NOT NULL,
  `rating_date` datetime(6) DEFAULT NULL,
  `object_pk` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `generic_rating_content_type_id_eaf475fa_fk_django_co` (`content_type_id`),
  KEY `generic_rating_user_id_60020469_fk_auth_user_id` (`user_id`),
  CONSTRAINT `generic_rating_content_type_id_eaf475fa_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `generic_rating_user_id_60020469_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `generic_threadedcomment`
--

DROP TABLE IF EXISTS `generic_threadedcomment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `generic_threadedcomment` (
  `comment_ptr_id` int(11) NOT NULL,
  `rating_count` int(11) NOT NULL,
  `rating_sum` int(11) NOT NULL,
  `rating_average` double NOT NULL,
  `by_author` tinyint(1) NOT NULL,
  `replied_to_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`comment_ptr_id`),
  KEY `generic_threadedcomm_replied_to_id_d0a08d73_fk_generic_t` (`replied_to_id`),
  CONSTRAINT `generic_threadedcomm_comment_ptr_id_e208ed60_fk_django_co` FOREIGN KEY (`comment_ptr_id`) REFERENCES `django_comments` (`id`),
  CONSTRAINT `generic_threadedcomm_replied_to_id_d0a08d73_fk_generic_t` FOREIGN KEY (`replied_to_id`) REFERENCES `generic_threadedcomment` (`comment_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_link`
--

DROP TABLE IF EXISTS `pages_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_link` (
  `page_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `pages_link_page_ptr_id_37d469f7_fk_pages_page_id` FOREIGN KEY (`page_ptr_id`) REFERENCES `pages_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_page`
--

DROP TABLE IF EXISTS `pages_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords_string` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) NOT NULL,
  `_meta_title` varchar(500) DEFAULT NULL,
  `description` longtext NOT NULL,
  `gen_description` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `short_url` varchar(200) DEFAULT NULL,
  `in_sitemap` tinyint(1) NOT NULL,
  `_order` int(11) DEFAULT NULL,
  `in_menus` varchar(100) DEFAULT NULL,
  `titles` varchar(1000) DEFAULT NULL,
  `content_model` varchar(50) DEFAULT NULL,
  `login_required` tinyint(1) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pages_page_parent_id_133fa4d3_fk_pages_page_id` (`parent_id`),
  KEY `pages_page_site_id_47a43e5b_fk_django_site_id` (`site_id`),
  KEY `pages_page_publish_date_eb7c8d46` (`publish_date`),
  CONSTRAINT `pages_page_parent_id_133fa4d3_fk_pages_page_id` FOREIGN KEY (`parent_id`) REFERENCES `pages_page` (`id`),
  CONSTRAINT `pages_page_site_id_47a43e5b_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_richtextpage`
--

DROP TABLE IF EXISTS `pages_richtextpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_richtextpage` (
  `page_ptr_id` int(11) NOT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `pages_richtextpage_page_ptr_id_8ca99b83_fk_pages_page_id` FOREIGN KEY (`page_ptr_id`) REFERENCES `pages_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `people_position`
--

DROP TABLE IF EXISTS `people_position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `people_position` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `title_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `people_position_title_id_01993333_fk_people_title_id` (`title_id`),
  KEY `people_position_user_id_fa85f5bf_fk_auth_user_id` (`user_id`),
  CONSTRAINT `people_position_title_id_01993333_fk_people_title_id` FOREIGN KEY (`title_id`) REFERENCES `people_title` (`id`),
  CONSTRAINT `people_position_user_id_fa85f5bf_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `people_profile`
--

DROP TABLE IF EXISTS `people_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `people_profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords_string` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) DEFAULT NULL,
  `_meta_title` varchar(500) DEFAULT NULL,
  `description` longtext NOT NULL,
  `gen_description` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `short_url` varchar(200) DEFAULT NULL,
  `in_sitemap` tinyint(1) NOT NULL,
  `education` longtext NOT NULL,
  `bio` longtext NOT NULL,
  `phone_number` varchar(50) NOT NULL,
  `office_location` varchar(255) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `thumb` varchar(255) DEFAULT NULL,
  `site_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `people_profile_site_id_4c91d416_fk_django_site_id` (`site_id`),
  KEY `people_profile_publish_date_97c838e5` (`publish_date`),
  CONSTRAINT `people_profile_site_id_4c91d416_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`),
  CONSTRAINT `people_profile_user_id_99bdfa5b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `people_profile_attachments`
--

DROP TABLE IF EXISTS `people_profile_attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `people_profile_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profile_id` int(11) NOT NULL,
  `attachment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `people_profile_attachmen_profile_id_attachment_id_c276a05f_uniq` (`profile_id`,`attachment_id`),
  KEY `people_profile_attac_attachment_id_57426842_fk_resources` (`attachment_id`),
  CONSTRAINT `people_profile_attac_attachment_id_57426842_fk_resources` FOREIGN KEY (`attachment_id`) REFERENCES `resources_attachment` (`id`),
  CONSTRAINT `people_profile_attac_profile_id_21aa9708_fk_people_pr` FOREIGN KEY (`profile_id`) REFERENCES `people_profile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `people_title`
--

DROP TABLE IF EXISTS `people_title`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `people_title` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `sort_order` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_grant`
--

DROP TABLE IF EXISTS `projects_grant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_grant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `grant_type_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projects_grant_grant_type_id_d2603942_fk_projects_granttype_id` (`grant_type_id`),
  KEY `projects_grant_project_id_97067bbe_fk_projects_project_id` (`project_id`),
  CONSTRAINT `projects_grant_grant_type_id_d2603942_fk_projects_granttype_id` FOREIGN KEY (`grant_type_id`) REFERENCES `projects_granttype` (`id`),
  CONSTRAINT `projects_grant_project_id_97067bbe_fk_projects_project_id` FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_granttype`
--

DROP TABLE IF EXISTS `projects_granttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_granttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grant_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `grant_type` (`grant_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_membership`
--

DROP TABLE IF EXISTS `projects_membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_membership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grant_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projects_membership_grant_id_3db9c231_fk_projects_grant_id` (`grant_id`),
  KEY `projects_membership_project_id_5f65bf3f_fk_projects_project_id` (`project_id`),
  KEY `projects_membership_role_id_c4bd36ef_fk_projects_role_id` (`role_id`),
  KEY `projects_membership_user_id_13374535_fk_auth_user_id` (`user_id`),
  CONSTRAINT `projects_membership_grant_id_3db9c231_fk_projects_grant_id` FOREIGN KEY (`grant_id`) REFERENCES `projects_grant` (`id`),
  CONSTRAINT `projects_membership_project_id_5f65bf3f_fk_projects_project_id` FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`),
  CONSTRAINT `projects_membership_role_id_c4bd36ef_fk_projects_role_id` FOREIGN KEY (`role_id`) REFERENCES `projects_role` (`id`),
  CONSTRAINT `projects_membership_user_id_13374535_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_project`
--

DROP TABLE IF EXISTS `projects_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords_string` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(2000) DEFAULT NULL,
  `_meta_title` varchar(500) DEFAULT NULL,
  `description` longtext NOT NULL,
  `gen_description` tinyint(1) NOT NULL,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `status` int(11) NOT NULL,
  `publish_date` datetime(6) DEFAULT NULL,
  `expiry_date` datetime(6) DEFAULT NULL,
  `short_url` varchar(200) DEFAULT NULL,
  `in_sitemap` tinyint(1) NOT NULL,
  `short_description` varchar(255) NOT NULL,
  `long_description` longtext NOT NULL,
  `highlight` tinyint(1) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `thumb` varchar(255) DEFAULT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projects_project_publish_date_f62e9f19` (`publish_date`),
  KEY `projects_project_site_id_81d4030f_fk_django_site_id` (`site_id`),
  CONSTRAINT `projects_project_site_id_81d4030f_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_project_attachments`
--

DROP TABLE IF EXISTS `projects_project_attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_project_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `attachment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `projects_project_attachm_project_id_attachment_id_186b0db4_uniq` (`project_id`,`attachment_id`),
  KEY `projects_project_att_attachment_id_9817c69c_fk_resources` (`attachment_id`),
  CONSTRAINT `projects_project_att_attachment_id_9817c69c_fk_resources` FOREIGN KEY (`attachment_id`) REFERENCES `resources_attachment` (`id`),
  CONSTRAINT `projects_project_att_project_id_1acc883f_fk_projects_` FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_projectresource`
--

DROP TABLE IF EXISTS `projects_projectresource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_projectresource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(200) NOT NULL,
  `project_id` int(11) NOT NULL,
  `resource_type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projects_projectreso_project_id_f9500731_fk_projects_` (`project_id`),
  KEY `projects_projectreso_resource_type_id_d3c92d3c_fk_resources` (`resource_type_id`),
  CONSTRAINT `projects_projectreso_project_id_f9500731_fk_projects_` FOREIGN KEY (`project_id`) REFERENCES `projects_project` (`id`),
  CONSTRAINT `projects_projectreso_resource_type_id_d3c92d3c_fk_resources` FOREIGN KEY (`resource_type_id`) REFERENCES `resources_resourcetype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects_role`
--

DROP TABLE IF EXISTS `projects_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `sort_order` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources_attachment`
--

DROP TABLE IF EXISTS `resources_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_attachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `file` varchar(255) NOT NULL,
  `url` varchar(200) NOT NULL,
  `attachment_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources_attachment_pages`
--

DROP TABLE IF EXISTS `resources_attachment_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_attachment_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attachment_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resources_attachment_pages_attachment_id_page_id_bbf1e7db_uniq` (`attachment_id`,`page_id`),
  KEY `resources_attachment_pages_page_id_72d6b977_fk_pages_page_id` (`page_id`),
  CONSTRAINT `resources_attachment_attachment_id_8cfc13a4_fk_resources` FOREIGN KEY (`attachment_id`) REFERENCES `resources_attachment` (`id`),
  CONSTRAINT `resources_attachment_pages_page_id_72d6b977_fk_pages_page_id` FOREIGN KEY (`page_id`) REFERENCES `pages_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources_landingpage`
--

DROP TABLE IF EXISTS `resources_landingpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_landingpage` (
  `page_ptr_id` int(11) NOT NULL,
  `content` longtext NOT NULL,
  `tagline` varchar(255) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`page_ptr_id`),
  CONSTRAINT `resources_landingpage_page_ptr_id_37b1fdb7_fk_pages_page_id` FOREIGN KEY (`page_ptr_id`) REFERENCES `pages_page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources_resourcetype`
--

DROP TABLE IF EXISTS `resources_resourcetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_resourcetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `sort_order` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `resources_userresource`
--

DROP TABLE IF EXISTS `resources_userresource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resources_userresource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(200) NOT NULL,
  `resource_type_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `resources_userresour_resource_type_id_63f23e74_fk_resources` (`resource_type_id`),
  KEY `resources_userresource_user_id_a4d2c37e_fk_auth_user_id` (`user_id`),
  CONSTRAINT `resources_userresour_resource_type_id_63f23e74_fk_resources` FOREIGN KEY (`resource_type_id`) REFERENCES `resources_resourcetype` (`id`),
  CONSTRAINT `resources_userresource_user_id_a4d2c37e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taggit_tag`
--

DROP TABLE IF EXISTS `taggit_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taggit_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `taggit_taggeditem`
--

DROP TABLE IF EXISTS `taggit_taggeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taggit_taggeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` (`tag_id`),
  KEY `taggit_taggeditem_object_id_e2d7d1df` (`object_id`),
  KEY `taggit_taggeditem_content_type_id_object_id_196cc965_idx` (`content_type_id`,`object_id`),
  CONSTRAINT `taggit_taggeditem_content_type_id_9957a03c_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `taggit_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-09 12:57:09
