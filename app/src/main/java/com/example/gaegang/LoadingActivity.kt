package com.example.gaegang

import android.app.Dialog
import android.content.Context
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.media.Image
import android.os.Bundle
import android.view.Window
import android.view.animation.Animation
import android.view.animation.AnimationUtils
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity

class LoadingActivity(context: Context) : Dialog(context) {
    private var c: Context? = null
    init{
        requestWindowFeature(Window.FEATURE_NO_TITLE)
        window!!.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        setCanceledOnTouchOutside(false)
        c = context
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_loading)

        val loadingImage= findViewById<ImageView>(R.id.loading_image)
        val anim : Animation = AnimationUtils.loadAnimation(c, R.anim.loading)
        loadingImage.animation = anim
    }
    override fun show(){
        super.show()
    }
    override fun dismiss() {
        super.dismiss()
    }
}