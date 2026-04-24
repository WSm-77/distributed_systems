module ServantsManagement {
    interface IntWrapperObject {
        int getValue();
        void setValue(int value);
    };

    interface Counter {
        long getCounter();
        void incrementCounter();
    };
};
