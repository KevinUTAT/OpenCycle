#include "config.h"
#include "ble_csc.h"

typedef struct {
    lv_obj_t *hour;
    lv_obj_t *minute;
    lv_obj_t *second;
} str_datetime_t;

static str_datetime_t g_data;
TTGOClass *watch = nullptr;
PCF8563_Class *rtc;

lv_obj_t * batV_label = nullptr;
lv_obj_t * rev_label = nullptr;
lv_obj_t * time_label = nullptr;
lv_obj_t * speed_label = nullptr;
lv_obj_t * dist_label = nullptr;

static unsigned start_rev = 0;

LV_FONT_DECLARE(morgnite_bold_64);
LV_FONT_DECLARE(oswald_regular_24);

void setup() {
    Serial.begin(115200);
    watch = TTGOClass::getWatch();
    watch->begin();
    watch->lvgl_begin();
    rtc = watch->rtc;
    // Use compile time
    rtc->check();

    watch->openBL();
    watch->bl->adjust(100);
    watch->tft->setRotation(1);
    watch->power->adc1Enable(AXP202_VBUS_VOL_ADC1 | 
      AXP202_VBUS_CUR_ADC1 | AXP202_BATT_CUR_ADC1 | AXP202_BATT_VOL_ADC1, true);


    create_status_bar();
    create_instruments();

    setup_ble_csc();
    setCpuFrequencyMhz(60);
}

void loop() {
    lv_task_handler();
    run_ble_csc();
}


void create_status_bar()
{
    // styles
    static lv_style_t background_style;
    lv_style_init(&background_style);
    lv_style_set_bg_color(&background_style, LV_STATE_DEFAULT, LV_COLOR_BLACK);
    lv_style_set_border_color(&background_style, LV_STATE_DEFAULT, LV_COLOR_BLACK);
    lv_style_set_border_width(&background_style, LV_STATE_DEFAULT, 1);

    static lv_style_t status_style;
    lv_style_init(&status_style);
    lv_style_set_text_color(&status_style, LV_STATE_DEFAULT, LV_COLOR_WHITE);
    lv_style_set_text_font(&status_style, LV_STATE_DEFAULT, &oswald_regular_24);

    static lv_style_t icon_style;
    lv_style_init(&icon_style);
    lv_style_set_text_color(&icon_style, LV_STATE_DEFAULT, LV_COLOR_WHITE);
    lv_style_set_text_font(&icon_style, LV_STATE_DEFAULT, &lv_font_montserrat_28);

    static lv_style_t bat_style;
    lv_style_init(&bat_style);
    lv_style_set_text_color(&bat_style, LV_STATE_DEFAULT, LV_COLOR_BLACK);
    lv_style_set_text_font(&bat_style, LV_STATE_DEFAULT, &lv_font_montserrat_12);

    // background
    lv_obj_t *status_bar = lv_obj_create(lv_scr_act(), NULL);
    lv_obj_add_style(status_bar, LV_OBJ_PART_MAIN, &background_style);
    lv_obj_set_size(status_bar, 250, 34);
    lv_obj_align(status_bar, NULL, LV_ALIGN_IN_TOP_MID, 0, 0);

    // logo
    lv_obj_t * logo_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(logo_label, LV_OBJ_PART_MAIN, &status_style);
    lv_label_set_text(logo_label, "OpenCycle");
    lv_obj_align(logo_label, nullptr, LV_ALIGN_IN_TOP_LEFT, 5, 5);

    // battery
    lv_obj_t * bat_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(bat_label, LV_OBJ_PART_MAIN, &icon_style);
    lv_label_set_text(bat_label, LV_SYMBOL_BATTERY_FULL);
    lv_obj_align(bat_label, nullptr, LV_ALIGN_IN_TOP_RIGHT, -5, 2);

    batV_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(batV_label, LV_OBJ_PART_MAIN, &bat_style);
    lv_label_set_text(batV_label, "99");
    lv_obj_align(batV_label, nullptr, LV_ALIGN_IN_TOP_RIGHT, -15, 10);

    lv_task_create([](lv_task_t *t) {
        lv_label_set_text_fmt(batV_label, "%02u", watch->power->getBattPercentage());
    }, 1000, LV_TASK_PRIO_MID, nullptr);

}


void create_instruments() {
    static lv_style_t debug_style;
    lv_style_init(&debug_style);
    lv_style_set_text_color(&debug_style, LV_STATE_DEFAULT, LV_COLOR_BLACK);
    lv_style_set_text_font(&debug_style, LV_STATE_DEFAULT, &oswald_regular_24);

    static lv_style_t data_style;
    lv_style_init(&data_style);
    lv_style_set_text_color(&data_style, LV_STATE_DEFAULT, LV_COLOR_BLACK);
    lv_style_set_text_font(&data_style, LV_STATE_DEFAULT, &morgnite_bold_64);

    //show denug datas
    rev_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(rev_label, LV_OBJ_PART_MAIN, &debug_style);
    lv_label_set_text(rev_label, "------");
    lv_obj_align(rev_label, nullptr, LV_ALIGN_IN_TOP_LEFT, 10, 44);

    time_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(time_label, LV_OBJ_PART_MAIN, &debug_style);
    lv_label_set_text(time_label, "------");
    lv_obj_align(time_label, nullptr, LV_ALIGN_IN_TOP_LEFT, 10, 76);

    // show datas
    speed_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(speed_label, LV_OBJ_PART_MAIN, &data_style);
    lv_label_set_text(speed_label, "------");
    lv_obj_align(speed_label, nullptr, LV_ALIGN_IN_TOP_LEFT, 10, 108);

    dist_label = lv_label_create(lv_scr_act(), NULL);
    lv_obj_add_style(dist_label, LV_OBJ_PART_MAIN, &data_style);
    lv_label_set_text(dist_label, "------");
    lv_obj_align(dist_label, nullptr, LV_ALIGN_IN_TOP_LEFT, 10, 174);

    lv_task_create([](lv_task_t *t) {
        lv_label_set_text_fmt(rev_label, "%08u", wheel_rev);
        lv_label_set_text_fmt(time_label, "%08u", last_wheel_time);
    }, 1000, LV_TASK_PRIO_MID, nullptr);

    run_instruments();
}


void run_instruments() {
    lv_task_create([](lv_task_t *t) {
        if ((prev_wheel_time == 0) && (prev_wheel_rev == 0)) {}// do nothing
        else {
            int d_rev = wheel_rev - prev_wheel_rev;
            int d_time = 0;
            if (last_wheel_time >= prev_wheel_time) {
                d_time = last_wheel_time - prev_wheel_time;
            }
            else {
                d_time = last_wheel_time + 65536 - prev_wheel_time;
            }
            if ((d_time > 0) && (d_rev < 100) && (d_rev > 0)) {
                float cur_rpm = ((float)d_rev / (float)d_time) * 61440.0;
                float cur_speed = (cur_rpm * 2155.0) / 16667.0;
                if (start_rev == 0){
                    start_rev = wheel_rev;
                }
                float distance = ((float)(wheel_rev - start_rev) * 2155.0) / 1000000.0;
                Serial.println(cur_speed);
                Serial.println(distance);
                Serial.println(d_rev);
                Serial.println(d_time);
                lv_label_set_text_fmt(speed_label, "%.02f", cur_speed);
                lv_label_set_text_fmt(dist_label, "%.02f", distance);
            }
        }
    }, 1000, LV_TASK_PRIO_MID, nullptr);
}

