package com.example.qr;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;

import com.squareup.picasso.Picasso;

public class ResultActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        Intent intent = getIntent();
        String image_url = "http://10.42.0.1:8000" + intent.getStringExtra("image_url");
        String laptop_name = intent.getStringExtra("laptop_name");
        String laptop_model = intent.getStringExtra("laptop_model");
        String serial_number = intent.getStringExtra("serial_number");
        String owner_first_name = intent.getStringExtra("owner_first_name");
        String occ = intent.getStringExtra("occ");
        String owner_id = intent.getStringExtra("owner_id");
        String dept = intent.getStringExtra("dept");
        ImageView imageView = findViewById(R.id.photo_image_view);
        TextView textView = findViewById(R.id.laptop_name);
        TextView textView10 = findViewById(R.id.laptop_model);
        TextView textView2 =findViewById(R.id.serial_number);
        TextView textView9 = findViewById(R.id.owner_first_name);
        TextView textView8 = findViewById(R.id.occ);
        TextView textView7 = findViewById(R.id.owner_id);


        textView.setText(laptop_name);
        textView10.setText(laptop_model);
        textView2.setText(serial_number);
        textView9.setText(owner_first_name);
        textView8.setText(occ);
        textView7.setText(owner_id);


        Picasso.get().load(image_url).into(imageView);
    }
}
